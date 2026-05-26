from pathlib import Path

from axionara.common.config import settings


class PromptLoader:
    def __init__(self, root_path: str | Path):
        self.root_path = self._normalize_root(root_path)

    def load(self, relative_path: str | Path) -> str:
        prompt_path = self._resolve_prompt_path(relative_path)
        content = prompt_path.read_text(encoding="utf-8").strip()
        if not content:
            raise ValueError(f"Prompt file is empty: {prompt_path}")
        return content

    @staticmethod
    def _normalize_root(root_path: str | Path) -> Path:
        root = Path(root_path).expanduser()
        if not root.is_absolute():
            root = Path.cwd() / root
        return root.resolve()

    def _resolve_prompt_path(self, relative_path: str | Path) -> Path:
        path = Path(relative_path)
        if path.is_absolute():
            raise ValueError("Prompt path must be relative to PROMPT_ROOT_PATH.")
        if path.suffix.lower() != ".md":
            raise ValueError("Prompt path must point to a markdown (.md) file.")

        prompt_path = (self.root_path / path).resolve()
        try:
            prompt_path.relative_to(self.root_path)
        except ValueError as exc:
            raise ValueError("Prompt path must stay inside PROMPT_ROOT_PATH.") from exc

        if not prompt_path.is_file():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        return prompt_path


def load_prompt(relative_path: str | Path) -> str:
    return PromptLoader(settings.PROMPT_ROOT_PATH).load(relative_path)


def load_agent_system_prompt() -> str:
    return load_prompt(settings.AGENT_SYSTEM_PROMPT_PATH)
