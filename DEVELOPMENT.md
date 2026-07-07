# Development

Implementation scaffolding for the benchmark specification in this repository.
**No normative pipeline code lands before implementation authorization**
(release plan V1-044); until then this tree holds layout, CI, config artifacts,
and skeleton suites only.

## Commands

```bash
pip install -e .[dev]     # install (core + dev tools); fresh clone must pass
ruff check .              # lint (Google-style docstrings enforced)
mypy                      # strict type checking over src/
pytest -q                 # test suite (skeleton until V1-044)
pip install -e .[pipeline]  # heavy pipeline deps (torch/transformers/bert-score)
```

## Layout

- `src/vlm_faithfulness_benchmark/<component>/` — one package per architecture
  component (C1–C8); see the Implementation Architecture design §2.
- `tests/<suite>/` — one suite per acceptance-matrix owner
  (`tests/ingestion` … `tests/views`, `tests/scoring`).
- `config/` — pinned config artifacts (e.g. the P2 pattern registry; hashes
  enter the Corpus Manifest integrity block).
- `data/`, `artifacts/` — git-ignored run outputs; manifests are committed,
  blobs are not.

## Standards

All code is bound by [CONTRIBUTING.md](CONTRIBUTING.md) "Code standards":
Google-style docstrings, PEP 484 type hints everywhere, math implemented from
scratch with the LaTeX formula in a comment directly above each implementation,
small testable units, and invariants encoded as asserts or dedicated tests
mapped in the V1-040 acceptance matrix.
