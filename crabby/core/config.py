from pathlib import Path
import platform
from typing import List, Optional

from dotenv import set_key
from pydantic_settings import BaseSettings, SettingsConfigDict

from crabby.core.exceptions import UnsupportedPlatformError


class Settings(BaseSettings):
    """
    Application configuration and filesystem settings.
    """

    INIT: bool = True

    CRABBY_DIR: Path = Path.home() / ".crabby"

    REMOTE_CONFIG_URL: str = ("https://raw.githubusercontent.com/cpadlab/crabby/main/config.example")

    SUPPORTED_PLATFORMS: List[str] = ["windows", "darwin"]

    WINDOW_TITLE: str = "Crabby"
    WINDOW_DEV_URL: str = "http://localhost:5173"
    WINDOW_WIDTH: int = 1200
    WINDOW_HEIGHT: int = 800
    WINDOW_MIN_WIDTH: int = 900
    WINDOW_MIN_HEIGHT: int = 600
    DEBUG: bool = True

    @property
    def ENV_FILE(self) -> Path:
        """Path: Target environment configuration file path."""
        return self.CRABBY_DIR / ".env"

    @property
    def EXAMPLE_FILE(self) -> Path:
        """
        Path: Reference example configuration file path.
        """
        return self.CRABBY_DIR / ".example"

    @property
    def LOGS_DIR(self) -> Path:
        """
        Path: Directory where rotated log files reside.
        """
        return self.CRABBY_DIR / "logs"

    @property
    def TEMPLATE_CONFIG_FILE(self) -> Path:
        """
        Path: Local template file in the root repository directory.
        """
        return Path(__file__).resolve().parent.parent.parent / "config.example"

    @property
    def FRONTEND_DIST_DIR(self) -> Path:
        """
        Path: Directory containing built frontend static files for production.
        """
        return Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

    @property
    def FRONTEND_INDEX_FILE(self) -> Path:
        """
        Path: Path to static index.html production entry file.
        """
        return self.FRONTEND_DIST_DIR / "index.html"

    @property
    def WINDOW_URL(self) -> str:
        """
        Resolves the target entry URL for pywebview.
        In production (when DEBUG is False and frontend/dist/index.html exists),
        returns the static index.html file path. Otherwise, returns WINDOW_DEV_URL.
        """
        if not self.DEBUG and self.FRONTEND_INDEX_FILE.exists():
            return str(self.FRONTEND_INDEX_FILE.resolve())
        return self.WINDOW_DEV_URL

    def validate_platform(self) -> str:
        """
        Validates that the current operating system is officially supported.

        Returns:
            str: The current system name if supported (e.g., 'windows' or 'darwin').

        Raises:
            UnsupportedPlatformError: If the operating system is not included
                in `SUPPORTED_PLATFORMS`.
        """
        current_os = platform.system().lower()
        
        if current_os not in self.SUPPORTED_PLATFORMS:
            supported = ", ".join(self.SUPPORTED_PLATFORMS)
            raise UnsupportedPlatformError(f"Platform '{current_os}' is not supported. Supported platforms: [{supported}]")
        
        return current_os

    def update_env(self, **kwargs) -> None:
        """Updates in-memory settings and persists them to the environment file.

        Sets each provided key-value pair as an attribute on the current instance
        and writes it directly to the file specified by `self.ENV_FILE` using
        `set_key`. If a value is `None`, it is saved as an empty string.

        Args:
            **kwargs: Arbitrary configuration key-value pairs to update and persist
                (e.g., `PET_POS_X=100`, `INIT=False`).
        """
        self.ENV_FILE.touch(exist_ok=True)

        for key, value in kwargs.items():
            setattr(self, key, value)
            set_key(str(self.ENV_FILE), key, str(value) if value is not None else "", quote_mode="never")


    model_config = SettingsConfigDict(
        env_file=str(Path.home() / ".crabby" / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()