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