from crabby.core.config import settings
from crabby.core.lifespan.startup import on_startup
from crabby.shared.logger import logger


def main() -> None:
    """
    Entry point for the Crabby desktop application.

    Executes the startup lifespan cycle, initializes the workspace and logging,
    and bootstraps the application context.
    """
    on_startup()


if __name__ == "__main__":
    main()