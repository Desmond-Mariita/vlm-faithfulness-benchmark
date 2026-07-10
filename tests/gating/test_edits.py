"""Tests for S09 edits and the P6 control edit (RIP §2.4, §2.6(d))."""

from __future__ import annotations

import numpy as np
import pytest

from vlm_faithfulness_benchmark.gating.edits import (
    apply_control_edit,
    apply_targeted_edit,
    control_box,
)
from vlm_faithfulness_benchmark.gating.saliency import EvidenceRegion, SaliencyGrid

GRID = SaliencyGrid(image_height=64, image_width=96)


def _region(box: tuple[int, int, int, int]) -> EvidenceRegion:
    mask = tuple(tuple(False for _ in range(8)) for _ in range(8))
    return EvidenceRegion(box=box, cell_mask=mask, max_drop=3.0, profile_id="test")


def _img(seed: int) -> np.ndarray:
    return np.random.default_rng(seed).integers(0, 256, (64, 96, 3), dtype=np.uint8)


def test_targeted_edit_changes_region_and_only_region_core() -> None:
    """The edit replaces the S08 box content; pixels outside stay identical."""
    img, partner = _img(1), _img(2)
    region = _region((16, 24, 32, 48))
    edited = apply_targeted_edit(img, partner, region, record_index=7)
    top, left, bottom, right = region.box
    assert not np.array_equal(edited[top:bottom, left:right], img[top:bottom, left:right])
    outside = edited.copy()
    outside[top:bottom, left:right] = img[top:bottom, left:right]
    assert np.array_equal(outside, img)
    assert np.array_equal(img, _img(1)), "source never mutated"


def test_edit_is_deterministic_per_record() -> None:
    """RIP §3: same record index => bit-identical edit; different => differs."""
    img, partner = _img(1), _img(2)
    region = _region((16, 24, 32, 48))
    a = apply_targeted_edit(img, partner, region, 7)
    b = apply_targeted_edit(img, partner, region, 7)
    c = apply_targeted_edit(img, partner, region, 8)
    assert np.array_equal(a, b)
    assert not np.array_equal(a, c)


def test_degenerate_region_is_conformance_error() -> None:
    """A broken S08 box halts; S09 never repairs or relocalizes (S09-pre)."""
    with pytest.raises(AssertionError):
        apply_targeted_edit(_img(1), _img(2), _region((10, 10, 10, 20)), 0)
    with pytest.raises(AssertionError):
        apply_targeted_edit(_img(1), _img(2), _region((0, 0, 100, 20)), 0)


def test_control_box_same_size_and_disjoint() -> None:
    """Control box matches size, is disjoint, and maximizes center distance."""
    region = _region((0, 0, 16, 24))  # top-left evidence
    box = control_box(region, 64, 96)
    ct, cl, cb, cr = box
    assert (cb - ct, cr - cl) == (16, 24)
    et, el, eb, er = region.box
    assert cb <= et or ct >= eb or cr <= el or cl >= er  # disjoint


def test_control_box_disjoint_even_for_large_evidence_region() -> None:
    """Review Blocker: a large evidence box must yield a DISJOINT placement."""
    region = _region((0, 0, 60, 90))  # nearly fills a 64x96 image -> no fit
    with pytest.raises(AssertionError, match="inapplicable"):
        control_box(region, 64, 96)
    region2 = _region((0, 0, 24, 96))  # full width, top strip; room only below
    box = control_box(region2, 64, 96)
    ct, cl, cb, cr = box
    et, el, eb, er = region2.box
    assert cb <= et or ct >= eb or cr <= el or cl >= er, "must be disjoint"
    assert (cb - ct, cr - cl) == (24, 96)


def test_control_box_inapplicable_when_evidence_fills_image() -> None:
    """No disjoint placement => assert; caller treats control as inapplicable."""
    with pytest.raises(AssertionError, match="inapplicable"):
        control_box(_region((0, 0, 64, 96)), 64, 96)


def test_control_edit_leaves_evidence_region_untouched() -> None:
    """The control edit never touches the evidence content it must avoid."""
    img, partner = _img(1), _img(2)
    region = _region((0, 0, 16, 24))
    edited = apply_control_edit(img, partner, region, 5)
    top, left, bottom, right = region.box
    assert np.array_equal(edited[top:bottom, left:right], img[top:bottom, left:right])
    assert not np.array_equal(edited, img)
