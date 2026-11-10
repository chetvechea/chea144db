"""Central configuration and runtime paths, independent of working directory."""

from dataclasses import dataclass, field
import os
import sys
from pathlib import Path


@dataclass(frozen=True)
class AutomationSettings:
    """Shared policy for future browser adapters; timeouts are milliseconds.

    Upload and publication waits are separate from ordinary interaction waits.
    Pacing supplements observable readiness checks; it does not replace them.
    """

    headless: bool = False
    action_timeout_ms: int = 30_000
    upload_timeout_ms: int = 300_000
    publish_confirmation_timeout_ms: int = 300_000
    click_delay_min_seconds: float = 1.0
    click_delay_max_seconds: float = 3.0


@dataclass(frozen=True)
class Settings:
    project_root: Path
    data_dir: Path
    log_dir: Path
    log_level: str
    app_name: str = "Social Media Auto Post Tool"
    automation: AutomationSettings = field(default_factory=AutomationSettings)

    @property
    def database_path(self) -> Path:
        return self.data_dir / "app.db"

    @property
    def profiles_dir(self) -> Path:
        return self.data_dir / "profiles"

    @property
    def media_dir(self) -> Path:
        return self.data_dir / "media"

    @property
    def artifacts_dir(self) -> Path:
        return self.data_dir / "artifacts"

    def ensure_directories(self) -> None:
        """Create runtime folders without creating the future database."""
        for directory in (
            self.data_dir, self.log_dir, self.profiles_dir,
            self.media_dir, self.artifacts_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)


def load_settings() -> Settings:
    root = Path(__file__).resolve().parents[2]
    if getattr(sys, "frozen", False):
        root = Path(os.environ["LOCALAPPDATA"]) / "SocialPoster"

    def configured_path(variable: str, default: str) -> Path:
        path = Path(os.environ.get(variable, default)).expanduser()
        return (path if path.is_absolute() else root / path).resolve()

    level = os.environ.get("SOCIAL_POSTER_LOG_LEVEL", "INFO").upper()
    if level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ValueError("SOCIAL_POSTER_LOG_LEVEL must be DEBUG, INFO, WARNING, ERROR, or CRITICAL.")
    return Settings(
        project_root=root,
        data_dir=configured_path("SOCIAL_POSTER_DATA_DIR", "data"),
        log_dir=configured_path("SOCIAL_POSTER_LOG_DIR", "logs"),
        log_level=level,
    )
