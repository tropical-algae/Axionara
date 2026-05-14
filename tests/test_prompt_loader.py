from pathlib import Path

import pytest

from axionara.core.prompt import PromptLoader


def test_prompt_loader_loads_markdown_prompt(tmp_path: Path):
    prompt_file = tmp_path / "agent" / "system.md"
    prompt_file.parent.mkdir()
    prompt_file.write_text("# Agent\n\nUse tools carefully.\n", encoding="utf-8")

    prompt = PromptLoader(tmp_path).load("agent/system.md")

    assert prompt == "# Agent\n\nUse tools carefully."


def test_prompt_loader_rejects_absolute_path(tmp_path: Path):
    prompt_file = tmp_path / "system.md"

    with pytest.raises(ValueError, match="relative"):
        PromptLoader(tmp_path).load(prompt_file)


def test_prompt_loader_rejects_path_traversal(tmp_path: Path):
    with pytest.raises(ValueError, match="inside"):
        PromptLoader(tmp_path).load("../system.md")


def test_prompt_loader_requires_markdown(tmp_path: Path):
    prompt_file = tmp_path / "system.txt"
    prompt_file.write_text("Use tools carefully.", encoding="utf-8")

    with pytest.raises(ValueError, match="markdown"):
        PromptLoader(tmp_path).load("system.txt")


def test_prompt_loader_rejects_empty_prompt(tmp_path: Path):
    prompt_file = tmp_path / "system.md"
    prompt_file.write_text("\n", encoding="utf-8")

    with pytest.raises(ValueError, match="empty"):
        PromptLoader(tmp_path).load("system.md")
