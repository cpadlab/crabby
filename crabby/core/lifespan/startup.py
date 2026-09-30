from pathlib import Path
import urllib.error
import urllib.request

from crabby.core.config import settings
from crabby.shared.logger import logger, setup_logger


def fetch_remote_config() -> str:
    """
    """
    try:
        req = urllib.request.Request(settings.REMOTE_CONFIG_URL, headers={"User-Agent": "Crabby-Desktop-App"})
        
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                logger.info(f"Template successfully downloaded from: {settings.REMOTE_CONFIG_URL}")
                return response.read().decode("utf-8")

    except (urllib.error.URLError, TimeoutError, Exception) as exc:
        logger.error(f"Error downloading remote template ({settings.REMOTE_CONFIG_URL}): {exc}")
        raise ConfigurationTemplateNotFoundError(f"The configuration template could not be downloaded from {settings.REMOTE_CONFIG_URL}") from exc

    raise ConfigurationTemplateNotFoundError(f"Unexpected response when downloading the template from {settings.REMOTE_CONFIG_URL}")


def init_workspace() -> Path:
    """
    """
    settings.CRABBY_DIR.mkdir(parents=True, exist_ok=True)
    settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)

    setup_logger()

    if settings.TEMPLATE_CONFIG_FILE.exists():
        template_content = settings.TEMPLATE_CONFIG_FILE.read_text(encoding="utf-8")
    else:
        logger.warning(f"{settings.TEMPLATE_CONFIG_FILE} was not found. Attempting remote download...")
        template_content = fetch_remote_config()

    settings.EXAMPLE_FILE.write_text(template_content, encoding="utf-8")

    if not settings.ENV_FILE.exists():
        settings.ENV_FILE.write_text(template_content, encoding="utf-8")
        logger.info(f"Initial configuration generated on: {settings.ENV_FILE}")
    else:
        logger.info(f"Settings loaded from: {settings.ENV_FILE}")

    return settings.ENV_FILE


def on_startup():
    """
    """
    init_workspace()
    logger.info("Ciclo de arranque de Crabby completado con éxito.")