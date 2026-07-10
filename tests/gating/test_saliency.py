"""Tests for S08 localization (matrix rows S08-post, BR-E5; fixture FX-N6)."""

from __future__ import annotations

import numpy as np
import pytest

from vlm_faithfulness_benchmark.gating.saliency import (
    GRID_COLS,
    GRID_ROWS,
    LOCALIZATION_PROFILE_ID,
    SaliencyGrid,
    localize,
)

GRID = SaliencyGrid(image_height=64, image_width=96)
FLOOR = 0.5


def _drops(**cells: float) -> np.ndarray:
    """Build a drops array with named hot cells, e.g. r2c3=4.0."""
    arr = np.zeros((GRID_ROWS, GRID_COLS), dtype=np.float64)
    for name, value in cells.items():
        r, c = int(name[1]), int(name[3])
        arr[r, c] = value
    return arr


def test_flat_saliency_yields_none_never_a_forced_box() -> None:
    """FX-N6: max drop below the floor => not locatable (E5, never D2)."""
    assert localize(_drops(r2c3=0.4), GRID, FLOOR) is None
    assert localize(np.zeros((GRID_ROWS, GRID_COLS)), GRID, FLOOR) is None


def test_single_hot_cell_boxes_that_cell() -> None:
    """The region is the hot cell's exact pixel box."""
    region = localize(_drops(r2c3=4.0), GRID, FLOOR)
    assert region is not None
    assert region.box == GRID.cell_box(2, 3)
    assert region.cell_mask[2][3] and sum(sum(r) for r in region.cell_mask) == 1
    assert region.max_drop == 4.0
    assert region.profile_id == LOCALIZATION_PROFILE_ID


def test_top_cells_within_half_of_max_join_the_box() -> None:
    """Cells >= 50% of the max drop are covered; weaker cells are not."""
    region = localize(_drops(r1c1=4.0, r3c4=2.5, r6c6=1.0), GRID, FLOOR)
    assert region is not None
    assert region.cell_mask[1][1] and region.cell_mask[3][4]
    assert not region.cell_mask[6][6]
    top, left, bottom, right = region.box
    assert (top, left) == GRID.cell_box(1, 1)[:2]
    assert (bottom, right) == GRID.cell_box(3, 4)[2:]


def test_malformed_or_nonfinite_sweep_is_conformance_error() -> None:
    """A broken sweep halts loudly; it is never read as flat saliency."""
    with pytest.raises(AssertionError):
        localize(np.zeros((4, 4)), GRID, FLOOR)
    bad = np.zeros((GRID_ROWS, GRID_COLS))
    bad[0, 0] = np.nan
    with pytest.raises(AssertionError, match="non-finite"):
        localize(bad, GRID, FLOOR)


def test_cell_occlusion_zeroes_exactly_one_cell() -> None:
    """The sweep input zeroes the target cell and nothing else."""
    img = np.full((64, 96, 3), 200, dtype=np.uint8)
    occluded = GRID.occlude_cell(img, 2, 3)
    top, left, bottom, right = GRID.cell_box(2, 3)
    assert (occluded[top:bottom, left:right] == 0).all()
    occluded[top:bottom, left:right] = 200
    assert np.array_equal(occluded, img)
    assert (img != 0).all(), "source image never mutated"
