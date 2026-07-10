"""S06 answer-side intervention regimes (RIP-1.0.0 §2.1; matrix rows S06-post, CC5, CC7).

The six-regime set per instance: ``real`` (unperturbed reference), four
information-destroying interventions (``grey``, ``wrong-image``, ``occlude``,
``noise``), and the semantics-preserving ``hflip`` negative control consumed
by P6 (RIP §2.6(a)).

Every stochastic regime draws from its own pinned, disjoint seed stream
keyed by the record index (RIP §2.1/§3), so perturbations are
bit-reproducible across runs and partitions. Images are HxWx3 uint8 arrays;
transforms never modify their input (a mutated source image would be a CC4
hazard one step downstream).
"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt

__all__ = ["REGIMES", "DESTRUCTIVE_REGIMES", "apply_regime", "wrong_image_partner_index"]

Image = npt.NDArray[np.uint8]

#: The pinned regime set, in canonical order (RIP §2.1).
REGIMES: tuple[str, ...] = ("real", "grey", "wrong-image", "occlude", "noise", "hflip")
#: The four information-destroying regimes Condition A reads (RIP §2.2).
DESTRUCTIVE_REGIMES: tuple[str, ...] = ("grey", "wrong-image", "occlude", "noise")

#: Pinned parameters (RIP §2.1).
_OCCLUDE_FRACTION = 0.5
_NOISE_SIGMA = 80.0
_GREY_VALUE = 128


def wrong_image_partner_index(sorted_position: int, dataset_size: int) -> int:
    """Return the derangement partner position for ``wrong-image`` (RIP §2.1).

    Within each source dataset, records are ordered by source-record
    identity; each image is replaced by its cyclic successor's image — a
    fixed derangement, identical across runs and partitions.

    LaTeX: partner(i) = (i + 1) mod N, a derangement for N >= 2.

    Args:
        sorted_position: The record's position in the identity-sorted order.
        dataset_size: Total records in the dataset (must be >= 2 so no image
            maps to itself).

    Returns:
        The partner's sorted position.

    Raises:
        AssertionError: If dataset_size < 2 or the position is out of range.
    """
    assert dataset_size >= 2, "derangement needs >= 2 records (no image maps to itself)"
    assert 0 <= sorted_position < dataset_size, "position out of range"
    return (sorted_position + 1) % dataset_size


def _occlude(image: Image, rng: np.random.Generator) -> Image:
    """Mask ~50% of the image area with a randomly-placed uint8 block grid.

    The mask layout is drawn from the pinned per-record stream; cells are
    16px squares toggled with probability 0.5 (expected coverage
    ``_OCCLUDE_FRACTION``), matching the legacy battery's coverage while
    remaining fully determined by the stream.
    """
    out = image.copy()
    cell = 16
    h, w = image.shape[:2]
    mask_rows = (h + cell - 1) // cell
    mask_cols = (w + cell - 1) // cell
    toggles = rng.random((mask_rows, mask_cols)) < _OCCLUDE_FRACTION
    for r in range(mask_rows):
        for c in range(mask_cols):
            if toggles[r, c]:
                out[r * cell : (r + 1) * cell, c * cell : (c + 1) * cell] = 0
    return out


def apply_regime(
    regime: str,
    image: Image,
    record_index: int,
    partner_image: Image | None = None,
) -> Image:
    """Apply one pinned regime transform to an image.

    Args:
        regime: One of ``REGIMES``.
        image: HxWx3 uint8 source image (never modified).
        record_index: The record index keying the pinned seed streams
            (occlude: ``default_rng(record_index)``; noise:
            ``default_rng(1_000_000 + record_index)`` — RIP §2.1).
        partner_image: The derangement partner's image; required for
            ``wrong-image`` only.

    Returns:
        The transformed image (a new array; ``real`` returns a copy).

    Raises:
        AssertionError: On an unknown regime, a malformed image, or a
            missing/present-when-unneeded partner image.
    """
    assert regime in REGIMES, f"unknown regime {regime!r}"
    assert image.ndim == 3 and image.shape[2] == 3 and image.dtype == np.uint8, (
        "image must be HxWx3 uint8"
    )
    assert (partner_image is not None) == (regime == "wrong-image"), (
        "partner_image is required for wrong-image and forbidden otherwise"
    )
    if regime == "real":
        return image.copy()
    if regime == "grey":
        return np.full_like(image, _GREY_VALUE)
    if regime == "wrong-image":
        assert partner_image is not None
        return partner_image.copy()
    if regime == "occlude":
        return _occlude(image, np.random.default_rng(record_index))
    if regime == "noise":
        rng = np.random.default_rng(1_000_000 + record_index)
        # LaTeX: x' = clip(x + \epsilon, 0, 255), \epsilon ~ N(0, \sigma^2), \sigma = 80
        noise = rng.normal(0.0, _NOISE_SIGMA, size=image.shape)
        return np.clip(image.astype(np.float64) + noise, 0, 255).astype(np.uint8)
    # hflip: horizontal mirror (semantics-preserving negative control).
    return image[:, ::-1, :].copy()
