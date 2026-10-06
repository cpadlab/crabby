from crabby.core.lifespan.startup import on_startup
from crabby.ui.window.controller import launch_window


def main() -> None:
    """
    Entry point for the Crabby desktop application.

    Executes the startup lifespan cycle, initializes the workspace and logging,
    and bootstraps the application context.
    """
    on_startup()
    launch_window()


if __name__ == "__main__":
    main()