"""Skeleton suite for component `ingestion` (owner per acceptance-matrix scheme)."""

import importlib


def test_component_package_imports() -> None:
    """The component package exists and imports cleanly."""
    mod = importlib.import_module("vlm_faithfulness_benchmark.ingestion")
    assert mod.__doc__ is not None
