from typing import Any, Dict, List, Optional

from pydantic import ValidationError

from crabby.controllers.mcp import MCPController
from crabby.schemas.mcp import HeaderItem, MCPServerCreate, MCPServerUpdate
from crabby.shared.logger import logger


class MCPBridge:
    """Synchronous PyWebView API for MCP server management."""

    def __init__(self) -> None:
        self.controller = MCPController()

    @staticmethod
    def _safe_error(exc: Exception) -> str:
        if isinstance(exc, ValidationError):
            errors = exc.errors(include_input=False)
            return "; ".join(item["msg"] for item in errors) or "MCP server details are invalid."
        if isinstance(exc, (ValueError, KeyError)):
            return str(exc)
        if isinstance(exc, RuntimeError):
            return "The secure credential store is unavailable. Check your operating-system keychain settings."
        return "The MCP operation failed. Check the server connection and credentials, then try again."

    @staticmethod
    def _parse_headers(data: Dict[str, Any]) -> Dict[str, Any]:
        payload = dict(data)
        if "headers" in payload and isinstance(payload["headers"], list):
            if any(not isinstance(header, dict) for header in payload["headers"]):
                raise ValueError("Each MCP header must contain a name and value.")
            payload["headers"] = [HeaderItem(**header) for header in payload["headers"]]
        return payload

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = self.controller.create(MCPServerCreate(**self._parse_headers(data)))
            return {"success": True, "data": response.model_dump()}
        except Exception as exc:
            logger.error("Error creating MCP server (%s).", type(exc).__name__)
            return {"success": False, "error": self._safe_error(exc)}

    def update(self, mcp_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = self.controller.update(mcp_id, MCPServerUpdate(**self._parse_headers(data)))
            return {"success": True, "data": response.model_dump()}
        except Exception as exc:
            logger.error("Error updating MCP server %s (%s).", mcp_id, type(exc).__name__)
            return {"success": False, "error": self._safe_error(exc)}

    def delete(self, mcp_id: str) -> Dict[str, Any]:
        try:
            return {"success": self.controller.delete(mcp_id)}
        except Exception as exc:
            logger.error("Error deleting MCP server %s (%s).", mcp_id, type(exc).__name__)
            return {"success": False, "error": self._safe_error(exc)}

    def check(self, mcp_id: str) -> Dict[str, Any]:
        try:
            return {"success": True, "connected": self.controller.check_connection(mcp_id)}
        except Exception as exc:
            return {"success": False, "connected": False, "error": self._safe_error(exc)}

    def check_by_url(
        self, url: str, headers: Optional[List[Dict[str, str]]] = None,
        timeout: float = 5.0, transport_type: str = "http",
    ) -> Dict[str, Any]:
        try:
            parsed_headers = [HeaderItem(**header) for header in (headers or [])]
            connected = MCPController.check_connection_by_url(url, parsed_headers, timeout, transport_type)
            return {"success": True, "connected": connected}
        except Exception as exc:
            return {"success": False, "connected": False, "error": self._safe_error(exc)}

    def discover_tools(self, mcp_id: str) -> Dict[str, Any]:
        try:
            tools = self.controller.discover_tools(mcp_id)
            return {"success": True, "data": [tool.model_dump() for tool in tools]}
        except Exception as exc:
            return {"success": False, "error": self._safe_error(exc)}

    def list_paginated(
        self, search: Optional[str] = None, page: int = 1, size: int = 10,
        sort_by: str = "created_at", sort_order: str = "desc",
    ) -> Dict[str, Any]:
        try:
            result = self.controller.list_paginated(search, page, size, sort_by, sort_order)
            return {"success": True, "data": result.model_dump()}
        except Exception as exc:
            logger.error("Error listing MCP servers (%s).", type(exc).__name__)
            return {"success": False, "error": self._safe_error(exc)}

    def get_ollama_tools(self) -> Dict[str, Any]:
        try:
            return {"success": True, "data": self.controller.get_all_ollama_tools()}
        except Exception as exc:
            return {"success": False, "error": self._safe_error(exc)}

    def execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        try:
            result = self.controller.execute_tool_call(tool_name, arguments)
            return {"success": True, "data": result.model_dump()}
        except Exception as exc:
            return {"success": False, "error": self._safe_error(exc)}
