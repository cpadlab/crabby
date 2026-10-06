import os
import sys
from pathlib import Path
import urllib.error
import urllib.request

from crabby.core.config import settings
from crabby.core.database import init_db
from crabby.core.exceptions import ConfigurationTemplateNotFoundError
from crabby.shared.logger import logger, setup_logger


def fetch_remote_config() -> str:
    """
    Fetches the default configuration template from the remote repository.

    Performs an HTTP GET request against the remote URL configured in settings
    with a 5-second timeout.

    Returns:
        str: Decoded UTF-8 text containing the raw configuration template.

    Raises:
        ConfigurationTemplateNotFoundError: If the network request fails, times out,
            or returns a non-200 HTTP status code.
    """
    try:
        req = urllib.request.Request(settings.REMOTE_CONFIG_URL, headers={"User-Agent": "Crabby-Desktop-App"},)

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
    Prepares the local Crabby workspace directory and configuration files.

    Creates required directories, sets up logging, synchronizes the `.example`
    reference template, and generates a `.env` file if one does not already exist.

    Returns:
        Path: Path to the active `.env` configuration file.

    Raises:
        ConfigurationTemplateNotFoundError: If local template resolution fails and
            the remote template cannot be retrieved.
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


def log_process_info() -> None:
    """
    Logs the current operating system process information.
    """
    pid = os.getpid()
    logger.info(f"Running Crabby process: PID-{pid}")


def on_startup() -> None:
    """
    Executes the startup sequence for the application lifespan.

    Initializes the workspace environment, confirms logging readiness, and
    emits the startup completion signal.
    """
    current_os = settings.validate_platform()

    init_workspace()
    init_db()
    log_process_info()

    logger.info(f"Platform detected and validated: {str(current_os).capitalize()}")

    logger.info("Crabby's startup cycle was successfully completed.")