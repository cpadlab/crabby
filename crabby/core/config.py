from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    
    INIT: bool = True

    CRABBY_DIR: Path = Path.home() / ".crabby"

    REMOTE_CONFIG_URL: str = "https://raw.githubusercontent.com/cpadlab/crabby/main/config.example"
    
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

    model_config = SettingsConfigDict(
        env_file=str(Path.home() / ".crabby" / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()