"""Checkpoint manager — save and load pipeline stage outputs as JSON."""
from pathlib import Path
from typing import Type, TypeVar

from pydantic import BaseModel

from app.lib.config import config

T = TypeVar("T", bound=BaseModel)

_DRAFTS_DIR = Path(config["paths"]["drafts_dir"])


def _stage_path(slug: str, stage_name: str) -> Path:
    return _DRAFTS_DIR / slug / f"{stage_name}.json"


def save(slug: str, stage_name: str, data: BaseModel) -> Path:
    """Serialize data to drafts/{slug}/{stage_name}.json. Returns the written path."""
    path = _stage_path(slug, stage_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data.model_dump_json(indent=2), encoding="utf-8")
    return path


def load(slug: str, stage_name: str, model_class: Type[T]) -> T | None:
    """Load and validate a checkpoint. Returns None if the file does not exist."""
    path = _stage_path(slug, stage_name)
    if not path.exists():
        return None
    return model_class.model_validate_json(path.read_text(encoding="utf-8"))
