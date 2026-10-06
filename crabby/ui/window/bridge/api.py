from crabby.ui.window.bridge.connections import ConnectionsBridge
from crabby.ui.window.bridge.mcp import MCPBridge


class WindowAPI:
    """
    Exposes Python backend methods and bridge modules to JavaScript via pywebview (js_api).
    """

    def __init__(self) -> None:
        self.connections = ConnectionsBridge()
        self.mcp = MCPBridge()

