"""Skeleton suite for the evaluation harness (tests/scoring owner rows)."""

import vlm_faithfulness_benchmark as pkg


def test_package_version_present() -> None:
    """Package exposes a version string."""
    assert isinstance(pkg.__version__, str) and pkg.__version__
