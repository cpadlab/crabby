import logging
from logging.handlers import TimedRotatingFileHandler

from crabby.core.config import settings

logger = logging.getLogger("crabby")


def setup_logger() -> None:
    """
    Configures application-wide logging handlers and formatters.

    Ensures the log directory exists and registers both a console stream
    handler and a daily midnight-rotating file handler if handlers are not
    already configured.

    Side Effects:
        Creates the directory specified by `settings.LOGS_DIR` on disk.
        Adds handlers to the module-level `logger` instance.
    """
    settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)

    log_path = settings.LOGS_DIR / "crabby.log"

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S",)

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        file_handler = TimedRotatingFileHandler(filename=str(log_path), when="midnight", interval=1, backupCount=30, encoding="utf-8")

        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)