"""S09 counterfactual-replacement edits and the P6 control edit (RIP §2.4, §2.6(d)).

Matrix rows: S09-pre/post, CC4 (consumes the exact S08 region; never
relocalizes), S10-post (control edit), D-ATOM (edit observations commit as
S09-family Intervention Records).

**Targeted edit (RIP §2.4):** the S08 region's content is replaced by the
same box coordinates cropped from the instance's ``wrong-image``
derangement partner, resized to the region — deterministic given the pinned
derangement. The seed stream ``default_rng(2_000_000 + record_index)``
covers only the pinned blend feathering.

**Control edit (RIP §2.6(d)):** the same machinery applied to a matched
non-evidence region — same box size, placed at maximal box-distance from
the evidence box within the image, seeded
``default_rng(3_000_000 + record_index)`` for its feathering. Control-edit
drift ≥ θ_B is a P6 failure (E6) evaluated before Condition B.
"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt

from vlm_faithfulness_benchmark.gating.saliency import EvidenceRegion

__all__ = ["apply_targeted_edit", "control_box", "apply_control_edit"]

Image = npt.NDArray[np.uint8]

#: Pinned feather width in pixels (blended border of the paste).
_FEATHER_PX = 3


def _resize_nearest(patch: Image, height: int, width: int) -> Image:
    """Resize a patch with nearest-neighbor sampling (pure numpy, pinned).

    Args:
        patch: Source patch (h, w, 3).
        height: Target height (>0).
        width: Target width (>0).
    """
    assert height > 0 and width > 0, "empty target box"
    src_h, src_w = patch.shape[:2]
    rows = (np.arange(height) * src_h // height).clip(0, src_h - 1)
    cols = (np.arange(width) * src_w // width).clip(0, src_w - 1)
    resized: Image = patch[rows][:, cols]
    return resized


def _paste_with_feather(
    image: Image, patch: Image, box: tuple[int, int, int, int], rng: np.random.Generator
) -> Image:
    """Paste ``patch`` into ``box`` with a feathered border (pinned blend).

    The feather blends patch and background linearly over ``_FEATHER_PX``
    border pixels; the rng draws only the per-edit feather phase (a scalar
    in [0.8, 1.0] scaling the border alpha), keeping the stream's role
    residual as RIP §2.4 pins.
    """
    top, left, bottom, right = box
    out = image.copy()
    region = patch.astype(np.float64)
    background = out[top:bottom, left:right].astype(np.float64)
    h, w = region.shape[:2]
    alpha = np.ones((h, w, 1), dtype=np.float64)
    phase = 0.8 + 0.2 * rng.random()
    for d in range(min(_FEATHER_PX, h // 2, w // 2)):
        edge_alpha = phase * (d + 1) / (_FEATHER_PX + 1)
        alpha[d, :], alpha[h - 1 - d, :] = edge_alpha, edge_alpha
        alpha[:, d], alpha[:, w - 1 - d] = (
            np.minimum(alpha[:, d], edge_alpha),
            np.minimum(alpha[:, w - 1 - d], edge_alpha),
        )
    blended = alpha * region + (1.0 - alpha) * background
    out[top:bottom, left:right] = np.clip(blended, 0, 255).astype(np.uint8)
    return out


def _donor_crop(partner_image: Image, box: tuple[int, int, int, int]) -> Image:
    """Crop the partner at the box coordinates, clipped to the partner's bounds.

    Falls back to the whole partner image when the clipped crop is empty
    (partner smaller than the box position) — the donor policy stays total.
    """
    top, left, bottom, right = box
    crop = partner_image[
        min(top, partner_image.shape[0]) : min(bottom, partner_image.shape[0]),
        min(left, partner_image.shape[1]) : min(right, partner_image.shape[1]),
    ]
    return crop if crop.size else partner_image


def apply_targeted_edit(
    image: Image,
    partner_image: Image,
    region: EvidenceRegion,
    record_index: int,
) -> Image:
    """Apply the S09 counterfactual replacement to the exact S08 region.

    Args:
        image: The baseline image (never modified).
        partner_image: The wrong-image derangement partner (RIP §2.1/§2.4).
        region: The exact S08 evidence region — consumed as-is, never
            relocalized (S09-pre).
        record_index: Keys the pinned feather stream
            ``default_rng(2_000_000 + record_index)``.

    Returns:
        The edited image.

    Raises:
        AssertionError: If the region box is degenerate or exceeds either
            image — a broken region is a conformance error at this boundary.
    """
    top, left, bottom, right = region.box
    assert 0 <= top < bottom <= image.shape[0] and 0 <= left < right <= image.shape[1], (
        "S09 consumes a well-formed S08 box within the image"
    )
    donor = _donor_crop(partner_image, region.box)
    patch = _resize_nearest(donor, bottom - top, right - left)
    rng = np.random.default_rng(2_000_000 + record_index)
    return _paste_with_feather(image, patch, region.box, rng)


def control_box(
    region: EvidenceRegion, image_height: int, image_width: int
) -> tuple[int, int, int, int]:
    """Place the control box: same size, maximal box-distance (RIP §2.6(d)).

    The control box has the evidence box's dimensions and is placed
    **disjoint** from the evidence box (review Blocker: a corner placement
    can overlap a large evidence region, corrupting the P6 attribution and
    the §5.1 separation evidence). Candidate placements sit fully above,
    below, left, or right of the evidence box, hugging the opposite image
    edge; the farthest-by-center-distance candidate wins. Deterministic, no
    stream needed.

    Args:
        region: The S08 evidence region.
        image_height: Image height in pixels.
        image_width: Image width in pixels.

    Returns:
        The control box ``(top, left, bottom, right)``.

    Raises:
        AssertionError: If the evidence box fills the image so no disjoint
            placement exists (the caller must treat the control as
            inapplicable, falling to the remaining P6 controls).
    """
    top, left, bottom, right = region.box
    box_h, box_w = bottom - top, right - left
    candidates: list[tuple[int, int]] = []
    if top >= box_h:  # fully above, hugging the top edge
        candidates.append((0, max(0, min(left, image_width - box_w))))
    if image_height - bottom >= box_h:  # fully below, hugging the bottom edge
        candidates.append((image_height - box_h, max(0, min(left, image_width - box_w))))
    if left >= box_w:  # fully to the left
        candidates.append((max(0, min(top, image_height - box_h)), 0))
    if image_width - right >= box_w:  # fully to the right
        candidates.append((max(0, min(top, image_height - box_h)), image_width - box_w))
    assert candidates, "no disjoint same-size placement exists; control edit inapplicable"
    center_r, center_c = (top + bottom) / 2, (left + right) / 2

    def _distance(pos: tuple[int, int]) -> float:
        cr, cc = pos[0] + box_h / 2, pos[1] + box_w / 2
        return (cr - center_r) ** 2 + (cc - center_c) ** 2

    best_top, best_left = max(candidates, key=_distance)
    chosen = (best_top, best_left, best_top + box_h, best_left + box_w)
    # Disjointness is load-bearing — assert it rather than trust the search.
    ct, cl, cb, cr2 = chosen
    assert cb <= top or ct >= bottom or cr2 <= left or cl >= right, (
        "control placement overlaps the evidence region (conformance error)"
    )
    return chosen


def apply_control_edit(
    image: Image,
    partner_image: Image,
    region: EvidenceRegion,
    record_index: int,
) -> Image:
    """Apply the evidence-irrelevant control edit (RIP §2.6(d)).

    Same machinery as the targeted edit, applied to the ``control_box``
    placement, feathered from ``default_rng(3_000_000 + record_index)``.

    Args:
        image: The baseline image (never modified).
        partner_image: The derangement partner (same donor policy).
        region: The S08 evidence region the control must avoid.
        record_index: Keys the control feather stream.

    Returns:
        The control-edited image.
    """
    box = control_box(region, image.shape[0], image.shape[1])
    top, left, bottom, right = box
    donor = _donor_crop(partner_image, box)
    patch = _resize_nearest(donor, bottom - top, right - left)
    rng = np.random.default_rng(3_000_000 + record_index)
    return _paste_with_feather(image, patch, box, rng)
