from typing import Any, Dict, List, Optional
from pydantic import ValidationError
from crabby.controllers.connections import ConnectionController
from crabby.schemas.connections import ConnectionCreate, ConnectionUpdate, HeaderItem
from crabby.shared.logger import logger


class ConnectionsBridge:
    """
    JS API Bridge namespace for connections.
    """

    def __init__(self) -> None:
        """
        """
        self.controller = ConnectionController()

    @staticmethod
    def _safe_error(exc: Exception) -> str:
        if isinstance(exc, ValidationError):
            details = exc.errors(include_input=False)
            return "; ".join(error["msg"] for error in details) or "Connection details are invalid."
        if isinstance(exc, (ValueError, KeyError)):
            return str(exc)
        return "The connection operation failed. Check the server and credentials, then try again."


    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a connection from JS payload.
        """
        try:
            if "headers" in data and isinstance(data["headers"], list):
                parsed_headers = []
                for h in data["headers"]:
                    if isinstance(h, dict):
                        parsed_headers.append(HeaderItem(**h))
                data["headers"] = parsed_headers

            create_schema = ConnectionCreate(**data)
            response = self.controller.create(create_schema)
            return {"success": True, "data": response.model_dump()}
        except Exception as exc:
            logger.error("Error creating connection (%s).", type(exc).__name__)
            return {"success": False, "error": self._safe_error(exc)}


    def update(self, conn_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates a connection from JS payload.
        """
        try:
            if "headers" in data and isinstance(data["headers"], list):
                parsed_headers = []
                for h in data["headers"]:
                    if isinstance(h, dict):
                        parsed_headers.append(HeaderItem(**h))
                data["headers"] = parsed_headers

            update_schema = ConnectionUpdate(**data)
            response = self.controller.update(conn_id, update_schema)
            return {"success": True, "data": response.model_dump()}
        except Exception as exc:
            logger.error("Error updating connection %s (%s).", conn_id, type(exc).__name__)
            return {"success": False, "error": self._safe_error(exc)}


    def delete(self, conn_id: str) -> Dict[str, Any]:
        """
        Deletes a connection by ID.
        """
        try:
            success = self.controller.delete(conn_id)
            return {"success": success}
        except Exception as exc:
            logger.error("Error deleting connection %s (%s).", conn_id, type(exc).__name__)
            return {"success": False, "error": self._safe_error(exc)}


    def check(self, conn_id: str) -> Dict[str, Any]:
        """
        Checks connectivity of a connection by ID.
        """
        try:
            is_alive = self.controller.check_connection(conn_id)
            return {"success": True, "connected": is_alive}
        except Exception as exc:
            return {"success": False, "connected": False, "error": self._safe_error(exc)}


    def check_by_url(self, host: str, headers: Optional[List[Dict[str, str]]] = None, timeout: float = 5.0) -> Dict[str, Any]:
        """
        Tests connectivity for an arbitrary host URL before saving.
        """
        try:
            header_items = [HeaderItem(**h) for h in (headers or [])]
            is_alive = ConnectionController.check_connection_by_url(host, header_items, timeout)
            return {"success": True, "connected": is_alive}
        except Exception as exc:
            return {"success": False, "connected": False, "error": self._safe_error(exc)}


    def get_models(self, conn_id: str) -> Dict[str, Any]:
        """
        Retrieves list of available models for a connection.
        """
        try:
            models = self.controller.get_models(conn_id)
            return {"success": True, "data": models}
        except Exception as exc:
            return {"success": False, "error": self._safe_error(exc)}


    def list_paginated(
        self,
        search: Optional[str] = None,
        page: int = 1,
        size: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """
        Lists paginated connections with search and sorting.
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
            logger.error("Error listing connections (%s).", type(exc).__name__)
            return {"success": False, "error": self._safe_error(exc)}
