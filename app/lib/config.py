from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import yaml

_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    anthropic_api_key: str = Field(default="")
    openai_api_key: str = Field(default="")
    cloudinary_cloud_name: str = Field(default="")
    cloudinary_api_key: str = Field(default="")
    cloudinary_api_secret: str = Field(default="")
    fg4b_website_path: str = Field(default="")


def load_config() -> dict:
    config_path = _ROOT / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


settings = Settings()
config = load_config()
