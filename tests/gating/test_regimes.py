"""Tests for the S06 regime transforms (RIP §2.1 pins; matrix rows S06-post, CC5)."""

from __future__ import annotations

import numpy as np
import pytest

from vlm_faithfulness_benchmark.gating.regimes import (
    DESTRUCTIVE_REGIMES,
    REGIMES,
    apply_regime,
    wrong_image_partner_index,
)


def _img(seed: int = 7) -> np.ndarray:
    return np.random.default_rng(seed).integers(0, 256, (64, 96, 3), dtype=np.uint8)


def test_regime_set_matches_rip_pin() -> None:
    """The pinned six-regime set, in canonical order."""
    assert REGIMES == ("real", "grey", "wrong-image", "occlude", "noise", "hflip")
    assert set(DESTRUCTIVE_REGIMES) < set(REGIMES)


def test_transforms_are_bit_reproducible() -> None:
    """RIP §3: seeded perturbations are bit-identical across calls."""
    img = _img()
    for regime in ("occlude", "noise"):
        a = apply_regime(regime, img, record_index=42)
        b = apply_regime(regime, img, record_index=42)
        assert np.array_equal(a, b), regime


def test_seed_streams_are_disjoint_by_record() -> None:
    """Different records draw different perturbations."""
    img = _img()
    assert not np.array_equal(
        apply_regime("noise", img, 1), apply_regime("noise", img, 2)
    )


def test_source_image_never_modified() -> None:
    """CC4 hazard guard: transforms never mutate their input."""
    img = _img()
    before = img.copy()
    for regime in REGIMES:
        partner = _img(9) if regime == "wrong-image" else None
        apply_regime(regime, img, 3, partner_image=partner)
    assert np.array_equal(img, before)


def test_hflip_is_an_involution_and_preserves_content() -> None:
    """The negative control mirrors; double application restores the image."""
    img = _img()
    flipped = apply_regime("hflip", img, 0)
    assert not np.array_equal(flipped, img)
    assert np.array_equal(apply_regime("hflip", flipped, 0), img)


def test_grey_is_information_free_and_occlude_covers_half() -> None:
    """grey = uniform field; occlude zeroes ~50% of pixels (pinned fraction)."""
    img = np.full((64, 96, 3), 200, dtype=np.uint8)
    grey = apply_regime("grey", img, 0)
    assert grey.min() == grey.max() == 128
    occluded = apply_regime("occlude", img, 5)
    zero_fraction = float((occluded == 0).mean())
    assert 0.3 < zero_fraction < 0.7, zero_fraction


def test_wrong_image_uses_partner_and_derangement_never_self_maps() -> None:
    """The derangement is cyclic-successor and total (no fixed point)."""
    img, partner = _img(1), _img(2)
    out = apply_regime("wrong-image", img, 0, partner_image=partner)
    assert np.array_equal(out, partner)
    for n in (2, 5, 1145):
        assert all(wrong_image_partner_index(i, n) != i for i in range(n))
    with pytest.raises(AssertionError):
        wrong_image_partner_index(0, 1)


def test_partner_image_required_exactly_for_wrong_image() -> None:
    """Partner presence is validated both ways."""
    img = _img()
    with pytest.raises(AssertionError):
        apply_regime("wrong-image", img, 0)
    with pytest.raises(AssertionError):
        apply_regime("grey", img, 0, partner_image=img)
