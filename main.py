from crabby.core.lifespan.startup import on_startup
from crabby.ui.pet.main import launch_pet


def main() -> None:
    """
    Entry point for the Crabby desktop application.

    Executes the startup lifespan cycle, initializes the workspace and logging,
    and bootstraps the application context.
    """
    on_startup()
    launch_pet()


if __name__ == "__main__":
    main()