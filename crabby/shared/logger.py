import logging
from logging.handlers import TimedRotatingFileHandler

from crabby.core.config import settings


logger = logging.getLogger("crabby")


def setup_logger():
    """
    """
    settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)

    log_path = settings.LOGS_DIR / "crabby.log"

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        file_handler = TimedRotatingFileHandler(
            filename=str(log_path), when="midnight", interval=1, backupCount=30, encoding="utf-8",
        )

        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)