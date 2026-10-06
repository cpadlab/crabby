from typing import Optional
import webview

from crabby.core.config import settings
from crabby.shared.logger import logger
from crabby.ui.window.api import WindowAPI


class WindowController:
    """
    Main controller for managing the pywebview desktop window lifecycle.
    """

    def __init__(
        self,
        title: Optional[str] = None,
        url: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        min_width: Optional[int] = None,
        min_height: Optional[int] = None,
    ) -> None:
        self.title = title or settings.WINDOW_TITLE
        self.url = url or settings.WINDOW_URL
        self.width = width or settings.WINDOW_WIDTH
        self.height = height or settings.WINDOW_HEIGHT
        self.min_width = min_width or settings.WINDOW_MIN_WIDTH
        self.min_height = min_height or settings.WINDOW_MIN_HEIGHT
        self.api = WindowAPI()
        self.window: Optional[webview.Window] = None


    def create_window(self) -> webview.Window:
        """
        Creates and configures the pywebview main window instance.

        Returns:
            webview.Window: The created pywebview window instance.
        """
        logger.info(f"Initializing main webview window '{self.title}' loading {self.url}")
        self.window = webview.create_window(
            title=self.title,
            url=self.url,
            width=self.width,
            height=self.height,
            min_size=(self.min_width, self.min_height),
            js_api=self.api,
            resizable=True,
        )
        return self.window


    def start(self, debug: Optional[bool] = None) -> None:
        """
        Launches the pywebview application event loop.

        Args:
            debug (Optional[bool]): Enables web view inspector if True. Defaults to settings.DEBUG.
        """
        if self.window is None:
            self.create_window()

        debug_flag = settings.DEBUG if debug is None else debug
        logger.info(f"Starting pywebview event loop (debug={debug_flag})...")
        webview.start(debug=debug_flag)


def launch_window(
    title: Optional[str] = None,
    url: Optional[str] = None,
    debug: Optional[bool] = None,
) -> None:
    """
    Helper function to initialize and start the Crabby desktop window.

    Args:
        title (Optional[str]): Window title bar string.
        url (Optional[str]): Target web app URL or local html entry file path.
        debug (Optional[bool]): Whether developer tools inspector should be active.
    """
    controller = WindowController(title=title, url=url)
    controller.start(debug=debug)
