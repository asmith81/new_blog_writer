"""Prompt loading and response cleaning utilities."""
import logging
from pathlib import Path
from string import Template

logger = logging.getLogger(__name__)

_PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "prompts"


def load_prompt(path: str | Path, **vars) -> str:
    """Read a prompt .txt file and substitute $variables using safe_substitute.

    Uses safe_substitute (not substitute) so that $WORD patterns inside
    user-supplied content (e.g. $4M, $USD) are left unchanged.
    """
    full_path = _PROMPTS_DIR / path if not Path(path).is_absolute() else Path(path)
    text = full_path.read_text(encoding="utf-8")
    return Template(text).safe_substitute(**vars)


def strip_fences(text: str) -> str:
    """Remove markdown code fences from LLM responses before json.loads().

    Handles:
        ```json\\n...\\n```
        ```\\n...\\n```
    Applied unconditionally — Claude intermittently wraps JSON even when told not to.
    """
    text = text.strip()
    if text.startswith("```"):
        # strip opening fence (```json or ```)
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1:]
        # strip closing fence
        if text.endswith("```"):
            text = text[: text.rfind("```")]
    return text.strip()
