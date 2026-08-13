"""Static guards for immutable Hugging Face revision loading (R3)."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

GENERATION_DIR = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "vlm_faithfulness_benchmark"
    / "generation"
)
ADAPTERS = (
    "qwen_generator.py",
    "glm_generator.py",
    "deepseek_generator.py",
    "kimi_generator.py",
    "gemma_generator.py",
)


@pytest.mark.parametrize("filename", ADAPTERS)
def test_every_from_pretrained_call_pins_revision(filename: str) -> None:
    """No adapter may resolve a moving Hub branch before recording its hash."""
    tree = ast.parse((GENERATION_DIR / filename).read_text(encoding="utf-8"))
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "from_pretrained"
    ]
    assert calls, f"{filename} contains no from_pretrained call"
    for call in calls:
        revision = next((kw.value for kw in call.keywords if kw.arg == "revision"), None)
        assert isinstance(revision, ast.Name) and revision.id == "_REVISION", (
            f"{filename}:{call.lineno} must pass revision=_REVISION"
        )


def test_kimi_bf16_loader_uses_transformers4_keyword() -> None:
    """Kimi's pinned Transformers 4.48 environment requires torch_dtype."""
    source = (GENERATION_DIR / "kimi_generator.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    bf16_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and any(kw.arg == "torch_dtype" for kw in node.keywords)
    ]
    assert bf16_calls, "Kimi bf16 load must pass torch_dtype, not dtype"
