"""S02 generation harness — one Output Tuple per (generator, source record).

Matrix rows: S02-post, S02-fail, S03-post, CC2/CC4/CC6, D-ATOM, D-ERR3, D-Q1.

The harness runs the composite generator once over a Source Record and
commits the Output Tuple **as emitted** — complete or not (ADR-003; no
drop, pad, or substitution) — atomically to the run ledger, keyed by the
instance identity. On resume, committed instances are skipped (GPU-run
discipline; `06a` R2). The DM Q1 baseline digest is computed inside the
same commit.

The generator itself is injected as a callable so the harness logic is
fully testable without model weights; the Qwen adapter lives in
``qwen_generator.py`` and is loaded only for real runs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Protocol

from vlm_faithfulness_benchmark.generation.digest import baseline_digest
from vlm_faithfulness_benchmark.generation.identity import GeneratorId, InstanceId
from vlm_faithfulness_benchmark.ingestion.aokvqa import SourceRecord
from vlm_faithfulness_benchmark.run_ledger import RunLedger

__all__ = ["GenerationOutcome", "GeneratorFn", "run_s02"]


@dataclass(frozen=True, slots=True)
class GenerationOutcome:
    """What one generator invocation emitted (possibly incomplete).

    Attributes:
        chosen_answer: The emitted answer text, or None if absent.
        rationale: The rationale object under the pinned `08` N4.6
            extraction contract, or None if absent.
    """

    chosen_answer: str | None
    rationale: str | None


class GeneratorFn(Protocol):
    """A composite generator invocation (same subject every call — CC7)."""

    def __call__(self, record: SourceRecord) -> GenerationOutcome:
        """Run the generator once over a Source Record."""
        ...


def run_s02(
    records: list[SourceRecord],
    generator: GeneratorFn,
    generator_id: GeneratorId,
    ledger: RunLedger,
    on_progress: Callable[[str], None] | None = None,
) -> Mapping[str, int]:
    """Execute S02 over a record batch, resumably.

    For each record: skip if committed (resume); otherwise invoke the
    generator exactly once and atomically commit the Output Tuple as
    emitted, with its baseline digest (DM Q1). An infrastructure exception
    from the generator leaves no committed record, so the invocation is
    retryable on the next run (design §5.3 / D-ERR3); the exception
    propagates — this harness never converts it into data.

    Args:
        records: Source Records to process (already normalized by S01).
        generator: The composite generator invocation.
        generator_id: The composite generator identity (recorded in the
            commit payload, never inside the Output Tuple fields — R6).
        ledger: The durable run ledger for this run scope.
        on_progress: Optional per-record progress callback.

    Returns:
        Counters: ``{"committed": n_new, "skipped": n_resumed}``.
    """
    committed = 0
    skipped = 0
    for record in records:
        instance = InstanceId(generator=generator_id, source=record.identity)
        key = f"{instance.key()}::output_tuple"
        if ledger.is_committed(key):
            skipped += 1
            continue
        outcome = generator(record)  # infra failure here -> no record, retryable
        output_tuple: dict[str, object] = {
            "chosen_answer": outcome.chosen_answer,
            "rationale": outcome.rationale,
        }
        ledger.commit(
            key,
            {
                "source": record.identity.key(),
                "generator": generator_id.key(),
                "output_tuple": output_tuple,
                "baseline_digest": baseline_digest(output_tuple),
            },
        )
        committed += 1
        if on_progress is not None:
            on_progress(f"{record.identity.key()} committed")
    return {"committed": committed, "skipped": skipped}
