"""Reader for FG4B_Website/data/content_index.json."""
import json
from pathlib import Path

from app.lib.config import settings


def load_content_index() -> dict:
    """Load and return the FG4B_Website content index.

    Raises RuntimeError with a clear message if FG4B_WEBSITE_PATH is not set
    or the file is missing.
    """
    if not settings.fg4b_website_path:
        raise RuntimeError(
            "FG4B_WEBSITE_PATH is not set in .env — cannot load content index."
        )
    path = Path(settings.fg4b_website_path) / "data" / "content_index.json"
    if not path.exists():
        raise RuntimeError(
            f"content_index.json not found at {path}. "
            "Verify FG4B_WEBSITE_PATH points to the FG4B_Website repo root."
        )
    return json.loads(path.read_text(encoding="utf-8"))
