from typing import Any, Dict, List, Optional

from crabby.controllers.mcp import MCPController
from crabby.schemas.mcp import HeaderItem, MCPServerCreate, MCPServerUpdate
from crabby.shared.logger import logger


class MCPBridge:
    """
    JS API Bridge namespace for remote MCP (Model Context Protocol) tool servers (`window.pywebview.api.mcp`).
    """

    def __init__(self) -> None:
        self.controller = MCPController()

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Registers a new MCP server from JS payload.
        """
        try:
            if "headers" in data and isinstance(data["headers"], list):
                parsed_headers = []
                for h in data["headers"]:
                    if isinstance(h, dict):
                        parsed_headers.append(HeaderItem(**h))
                data["headers"] = parsed_headers

            create_schema = MCPServerCreate(**data)
            response = self.controller.create(create_schema)
            return {"success": True, "data": response.model_dump()}
        except Exception as exc:
            logger.error(f"Error creating MCP server: {exc}")
            return {"success": False, "error": str(exc)}

    def update(self, mcp_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates an existing MCP server from JS payload.
        """
        try:
            if "headers" in data and isinstance(data["headers"], list):
                parsed_headers = []
                for h in data["headers"]:
                    if isinstance(h, dict):
                        parsed_headers.append(HeaderItem(**h))
                data["headers"] = parsed_headers

            update_schema = MCPServerUpdate(**data)
            response = self.controller.update(mcp_id, update_schema)
            return {"success": True, "data": response.model_dump()}
        except Exception as exc:
            logger.error(f"Error updating MCP server {mcp_id}: {exc}")
            return {"success": False, "error": str(exc)}

    def delete(self, mcp_id: str) -> Dict[str, Any]:
        """
        Deletes an MCP server by ID.
        """
        try:
            success = self.controller.delete(mcp_id)
            return {"success": success}
        except Exception as exc:
            logger.error(f"Error deleting MCP server {mcp_id}: {exc}")
            return {"success": False, "error": str(exc)}

    def check(self, mcp_id: str) -> Dict[str, Any]:
        """
        Checks connectivity of an MCP server by ID.
        """
        try:
            is_alive = self.controller.check_connection(mcp_id)
            return {"success": True, "connected": is_alive}
        except Exception as exc:
            return {"success": False, "connected": False, "error": str(exc)}

    def check_by_url(self, url: str, headers: Optional[List[Dict[str, str]]] = None, timeout: float = 5.0) -> Dict[str, Any]:
        """
        Tests connectivity for an arbitrary MCP URL before saving.
        """
        try:
            header_items = [HeaderItem(**h) for h in (headers or [])]
            is_alive = MCPController.check_connection_by_url(url, header_items, timeout)
            return {"success": True, "connected": is_alive}
        except Exception as exc:
            return {"success": False, "connected": False, "error": str(exc)}

    def discover_tools(self, mcp_id: str) -> Dict[str, Any]:
        """
        Discovers exposed tools from an MCP server.
        """
        try:
            tools = self.controller.discover_tools(mcp_id)
            return {"success": True, "data": [t.model_dump() for t in tools]}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def list_paginated(
        self,
        search: Optional[str] = None,
        page: int = 1,
        size: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """
        Lists paginated MCP servers with search and sorting.
        """
        try:
            response = self.controller.list_paginated(
                search=search,
                page=page,
                size=size,
                sort_by=sort_by,
                sort_order=sort_order,
            )
            return {"success": True, "data": response.model_dump()}
        except Exception as exc:
            logger.error(f"Error listing MCP servers: {exc}")
            return {"success": False, "error": str(exc)}

    def get_ollama_tools(self) -> Dict[str, Any]:
        """
        Returns all discovered tools formatted as an Ollama-compatible tools payload.
        """
        try:
            tools = self.controller.get_all_ollama_tools()
            return {"success": True, "data": tools}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a tool call invoked by Ollama LLM.
        """
        try:
            result = self.controller.execute_tool_call(tool_name, arguments)
            return {"success": True, "data": result.model_dump()}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

