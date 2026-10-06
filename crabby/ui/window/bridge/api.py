from crabby.ui.window.bridge.connections import ConnectionsBridge


class WindowAPI:
    """
    Exposes Python backend methods and bridge modules to JavaScript via pywebview (js_api).
    """

    def __init__(self) -> None:
        self.connections = ConnectionsBridge()

