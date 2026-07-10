"""S08 evidence localization — occlusion-saliency sweep (RIP-1.0.0 §2.3).

Matrix rows: S08-post, S08-trace, BR-E5, E5≠D2; V1-012 (candidate-scoped,
stable, audit-resolvable region identity).

The sweep occludes one grid cell at a time and scores the drop in the
baseline-chosen option's log-likelihood; the answer-relevant region is the
smallest axis-aligned bounding box covering the top-saliency cells. If the
maximum cell drop falls below the calibrated flat-saliency floor, the
evidence is **not locatable** → P5 fail → E5 (never a forced box, never
D2).

This module owns the pure geometry/decision logic; the per-cell scoring
(one generator call per cell) is injected, so the logic is fully testable
without weights. The localization profile identifier is recorded with every
region (S08-trace).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

__all__ = ["LOCALIZATION_PROFILE_ID", "SaliencyGrid", "EvidenceRegion", "localize"]

Image = npt.NDArray[np.uint8]

#: Implementation-owned localization profile (recorded in provenance, S08-trace).
LOCALIZATION_PROFILE_ID = "occlusion-grid-8x8-topq-v1"
#: Pinned sweep grid (RIP §2.3: "regular grid ... pinned in the implementation config").
GRID_ROWS, GRID_COLS = 8, 8
#: Top-saliency cell selection: cells within this fraction of the max drop.
TOP_CELL_FRACTION = 0.5


@dataclass(frozen=True, slots=True)
class SaliencyGrid:
    """The pinned sweep grid over one image.

    Attributes:
        image_height: Source image height in pixels.
        image_width: Source image width in pixels.
    """

    image_height: int
    image_width: int

    def cell_box(self, row: int, col: int) -> tuple[int, int, int, int]:
        """Return one cell's pixel box ``(top, left, bottom, right)`` (exclusive).

        Args:
            row: Cell row in ``[0, GRID_ROWS)``.
            col: Cell column in ``[0, GRID_COLS)``.
        """
        assert 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS, "cell out of grid"
        top = row * self.image_height // GRID_ROWS
        bottom = (row + 1) * self.image_height // GRID_ROWS
        left = col * self.image_width // GRID_COLS
        right = (col + 1) * self.image_width // GRID_COLS
        return (top, left, bottom, right)

    def occlude_cell(self, image: Image, row: int, col: int) -> Image:
        """Return a copy of ``image`` with one cell zeroed (the sweep input)."""
        top, left, bottom, right = self.cell_box(row, col)
        out = image.copy()
        out[top:bottom, left:right] = 0
        return out


@dataclass(frozen=True, slots=True)
class EvidenceRegion:
    """The candidate-scoped evidence-region identity (V1-012; S08-post).

    Attributes:
        box: Pixel box ``(top, left, bottom, right)`` — the smallest
            axis-aligned box covering the top-saliency cells.
        cell_mask: GRID_ROWS x GRID_COLS booleans marking the top cells
            (the audit-resolvable basis of the box).
        max_drop: The maximum per-cell log-likelihood drop observed (CC5).
        profile_id: The localization profile that produced this region.
    """

    box: tuple[int, int, int, int]
    cell_mask: tuple[tuple[bool, ...], ...]
    max_drop: float
    profile_id: str


# LaTeX: drop_{rc} = s_{\text{base}} - s_{rc};\; \text{locatable} \iff \max_{rc} drop_{rc} \ge \tau
# with \tau the calibrated flat-saliency floor (RIP §2.3/§5.2).
def localize(
    cell_drops: npt.NDArray[np.float64],
    grid: SaliencyGrid,
    flat_saliency_floor: float,
) -> EvidenceRegion | None:
    """Decide locatability and build the evidence region from sweep drops.

    Args:
        cell_drops: GRID_ROWS x GRID_COLS array; entry (r, c) is the drop in
            the baseline-chosen option's log-likelihood when cell (r, c) is
            occluded (baseline score minus occluded score).
        grid: The sweep grid the drops were measured on.
        flat_saliency_floor: The calibrated floor τ (RIP §5.2); below it the
            evidence is not locatable.

    Returns:
        The EvidenceRegion, or None when saliency is flat — the caller
        routes P5 fail → E5 (never a forced box, never D2).

    Raises:
        AssertionError: On a malformed drops array or non-finite values —
            a broken sweep is a conformance error, not "flat saliency".
    """
    assert cell_drops.shape == (GRID_ROWS, GRID_COLS), "drops must cover the pinned grid"
    assert np.isfinite(cell_drops).all(), "non-finite sweep drops are a conformance error"

    max_drop = float(cell_drops.max())
    if max_drop < flat_saliency_floor:
        return None

    threshold = max_drop * TOP_CELL_FRACTION
    top_cells = cell_drops >= threshold
    rows, cols = np.nonzero(top_cells)
    boxes = [grid.cell_box(int(r), int(c)) for r, c in zip(rows, cols)]
    box = (
        min(b[0] for b in boxes),
        min(b[1] for b in boxes),
        max(b[2] for b in boxes),
        max(b[3] for b in boxes),
    )
    return EvidenceRegion(
        box=box,
        cell_mask=tuple(tuple(bool(v) for v in row) for row in top_cells),
        max_drop=max_drop,
        profile_id=LOCALIZATION_PROFILE_ID,
    )
