from pathlib import Path
import platform
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

from crabby.core.exceptions import UnsupportedPlatformError


class Settings(BaseSettings):
    
    INIT: bool = True

    CRABBY_DIR: Path = Path.home() / ".crabby"

    REMOTE_CONFIG_URL: str = "https://raw.githubusercontent.com/cpadlab/crabby/main/config.example"
    SUPPORTED_PLATFORMS: List[str] = ["windows", "darwin"]
    
    @property
    def ENV_FILE(self) -> Path:
        return self.CRABBY_DIR / ".env"

    @property
    def EXAMPLE_FILE(self) -> Path:
        return self.CRABBY_DIR / ".example"

    @property
    def LOGS_DIR(self) -> Path:
        return self.CRABBY_DIR / "logs"

    @property
    def TEMPLATE_CONFIG_FILE(self) -> Path:
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
            raise UnsupportedPlatformError(
                f"Platform '{current_os}' is not supported. Supported platforms: [{supported}]"
            )
        return current_os

    model_config = SettingsConfigDict(
        env_file=str(Path.home() / ".crabby" / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()