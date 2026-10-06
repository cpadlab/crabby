import json
import math
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from crabby.core.database import get_connection
from crabby.schemas.mcp import (
    HeaderItem,
    MCPServerCreate,
    MCPServerResponse,
    MCPServerUpdate,
    MCPToolDefinition,
    PaginatedMCPServersResponse,
    ToolExecutionResult,
)
from crabby.shared.logger import logger


class MCPController:
    """
    Decoupled controller for managing static remote MCP (Model Context Protocol) tool endpoints,
    discovering exposed tools, formatting them for Ollama LLM tool calling, and executing remote tool calls.
    """

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _normalize_url(url: str) -> str:
        clean = url.strip().rstrip("/")
        if not clean.startswith(("http://", "https://")):
            clean = f"http://{clean}"
        return clean

    @classmethod
    def _build_request_headers(cls, headers: List[HeaderItem]) -> Dict[str, str]:
        req_headers: Dict[str, str] = {
            "User-Agent": "Crabby-Desktop-App/1.0",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        for item in headers:
            if item.key and item.value:
                req_headers[item.key] = item.value
        return req_headers

    @classmethod
    def _send_http_request(
        cls,
        url: str,
        method: str = "GET",
        headers: Optional[List[HeaderItem]] = None,
        payload: Optional[Dict[str, Any]] = None,
        timeout: float = 5.0,
    ) -> Dict[str, Any]:
        req_headers = cls._build_request_headers(headers or [])
        data_bytes = json.dumps(payload).encode("utf-8") if payload is not None else None

        req = urllib.request.Request(url, data=data_bytes, headers=req_headers, method=method)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            if not body.strip():
                return {}
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                return {"raw_response": body}

    @classmethod
    def check_connection_by_url(cls, url: str, headers: List[HeaderItem], timeout: float = 5.0) -> bool:
        """
        Tests if a remote MCP endpoint is online and reachable.
        Checks base URL or health / tools endpoint.
        """
        clean_url = cls._normalize_url(url)
        endpoints_to_try = [
            f"{clean_url}/health",
            f"{clean_url}/tools",
            clean_url,
        ]

        for ep in endpoints_to_try:
            try:
                cls._send_http_request(ep, method="GET", headers=headers, timeout=timeout)
                return True
            except Exception:
                continue

        try:
            rpc_payload = {"jsonrpc": "2.0", "method": "tools/list", "id": 1}
            cls._send_http_request(clean_url, method="POST", headers=headers, payload=rpc_payload, timeout=timeout)
            return True
        except Exception as exc:
            logger.debug(f"MCP health check failed for '{clean_url}': {exc}")
            return False

    @classmethod
    def discover_tools_by_url(
        cls, url: str, headers: List[HeaderItem], timeout: float = 5.0, server_id: Optional[str] = None, server_name: Optional[str] = None
    ) -> List[MCPToolDefinition]:
        """
        Queries a remote MCP endpoint to discover exposed tools and functions.
        Supports REST endpoints (/tools), JSON-RPC 2.0 (tools/list), and OpenAPI specs.
        """
        clean_url = cls._normalize_url(url)
        discovered_tools: List[MCPToolDefinition] = []

        try:
            res = cls._send_http_request(f"{clean_url}/tools", method="GET", headers=headers, timeout=timeout)
            tools_list = res.get("tools") if isinstance(res, dict) else None
            if isinstance(tools_list, list):
                for item in tools_list:
                    if isinstance(item, dict) and "name" in item:
                        discovered_tools.append(
                            MCPToolDefinition(
                                name=item["name"],
                                description=item.get("description", ""),
                                parameters=item.get("parameters") or item.get("inputSchema") or {"type": "object", "properties": {}},
                                server_id=server_id,
                                server_name=server_name,
                            )
                        )
                if discovered_tools:
                    return discovered_tools
        except Exception:
            pass

        try:
            rpc_payload = {"jsonrpc": "2.0", "method": "tools/list", "id": 1}
            res = cls._send_http_request(clean_url, method="POST", headers=headers, payload=rpc_payload, timeout=timeout)
            result = res.get("result", {}) if isinstance(res, dict) else {}
            tools_list = result.get("tools") if isinstance(result, dict) else None
            if isinstance(tools_list, list):
                for item in tools_list:
                    if isinstance(item, dict) and "name" in item:
                        discovered_tools.append(
                            MCPToolDefinition(
                                name=item["name"],
                                description=item.get("description", ""),
                                parameters=item.get("inputSchema") or item.get("parameters") or {"type": "object", "properties": {}},
                                server_id=server_id,
                                server_name=server_name,
                            )
                        )
                if discovered_tools:
                    return discovered_tools
        except Exception:
            pass

        return discovered_tools

    def create(self, data: MCPServerCreate) -> MCPServerResponse:
        """
        Registers a new remote MCP server connection.
        """
        if not data.name or not data.name.strip():
            raise ValueError("MCP server name cannot be empty.")
        if not data.url or not data.url.strip():
            raise ValueError("MCP server URL cannot be empty.")

        data.url = self._normalize_url(data.url)

        if not self.check_connection_by_url(data.url, data.headers, data.timeout):
            raise ValueError(f"Could not connect to MCP server at '{data.url}'. Check URL and network permissions.")

        now = self._now_iso()
        server_id = f"mcp_{uuid.uuid4().hex[:12]}"
        headers_json = json.dumps([h.model_dump() for h in data.headers])

        with get_connection() as db_conn:
            cursor = db_conn.cursor()

            cursor.execute("SELECT id FROM mcp_servers WHERE LOWER(name) = LOWER(?)", (data.name.strip(),))
            if cursor.fetchone():
                raise ValueError(f"An MCP server with the name '{data.name.strip()}' already exists.")

            cursor.execute(
                """
                INSERT INTO mcp_servers (id, name, type, url, headers, timeout, enabled, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (server_id, data.name.strip(), data.type, data.url, headers_json, data.timeout, 1 if data.enabled else 0, now, now),
            )
            db_conn.commit()

        logger.info(f"Registered new MCP server '{data.name}' (ID: {server_id})")
        tools = self.discover_tools_by_url(data.url, data.headers, data.timeout, server_id=server_id, server_name=data.name.strip())

        return MCPServerResponse(
            id=server_id,
            name=data.name.strip(),
            type=data.type,
            url=data.url,
            headers=data.headers,
            timeout=data.timeout,
            enabled=data.enabled,
            created_at=now,
            updated_at=now,
            tools=tools,
        )

    def update(self, server_id: str, data: MCPServerUpdate) -> MCPServerResponse:
        """
        Updates an existing MCP server registration.
        """
        now = self._now_iso()

        with get_connection() as db_conn:
            cursor = db_conn.cursor()
            cursor.execute("SELECT * FROM mcp_servers WHERE id = ?", (server_id,))
            row = cursor.fetchone()
            if not row:
                raise KeyError(f"MCP server with ID '{server_id}' not found.")

            current_name = row["name"]
            new_name = data.name.strip() if data.name and data.name.strip() else current_name

            if new_name.lower() != current_name.lower():
                cursor.execute("SELECT id FROM mcp_servers WHERE LOWER(name) = LOWER(?) AND id != ?", (new_name, server_id))
                if cursor.fetchone():
                    raise ValueError(f"An MCP server with the name '{new_name}' already exists.")

            new_type = data.type if data.type else row["type"]
            new_url = self._normalize_url(data.url) if data.url and data.url.strip() else row["url"]
            new_timeout = data.timeout if data.timeout is not None and data.timeout > 0 else row["timeout"]
            new_enabled = data.enabled if data.enabled is not None else bool(row["enabled"])

            if data.headers is not None:
                new_headers = data.headers
                headers_json = json.dumps([h.model_dump() for h in new_headers])
            else:
                new_headers = [HeaderItem(**h) for h in json.loads(row["headers"])]
                headers_json = row["headers"]

            cursor.execute(
                """
                UPDATE mcp_servers
                SET name = ?, type = ?, url = ?, headers = ?, timeout = ?, enabled = ?, updated_at = ?
                WHERE id = ?
                """,
                (new_name, new_type, new_url, headers_json, new_timeout, 1 if new_enabled else 0, now, server_id),
            )
            db_conn.commit()

        tools = self.discover_tools_by_url(new_url, new_headers, new_timeout, server_id=server_id, server_name=new_name)

        return MCPServerResponse(
            id=server_id,
            name=new_name,
            type=new_type,
            url=new_url,
            headers=new_headers,
            timeout=new_timeout,
            enabled=new_enabled,
            created_at=row["created_at"],
            updated_at=now,
            tools=tools,
        )

    def delete(self, server_id: str) -> bool:
        """
        Deletes an MCP server record by ID.
        """
        with get_connection() as db_conn:
            cursor = db_conn.cursor()
            cursor.execute("DELETE FROM mcp_servers WHERE id = ?", (server_id,))
            db_conn.commit()
            if cursor.rowcount == 0:
                raise KeyError(f"MCP server with ID '{server_id}' not found.")

        logger.info(f"Deleted MCP server ID '{server_id}'")
        return True

    def get_by_id(self, server_id: str) -> Optional[MCPServerResponse]:
        """
        Retrieves a single MCP server record with tools.
        """
        with get_connection() as db_conn:
            cursor = db_conn.cursor()
            cursor.execute("SELECT * FROM mcp_servers WHERE id = ?", (server_id,))
            row = cursor.fetchone()
            if not row:
                return None

            headers = [HeaderItem(**h) for h in json.loads(row["headers"])]
            tools = self.discover_tools_by_url(row["url"], headers, row["timeout"], server_id=row["id"], server_name=row["name"])

            return MCPServerResponse(
                id=row["id"],
                name=row["name"],
                type=row["type"],
                url=row["url"],
                headers=headers,
                timeout=row["timeout"],
                enabled=bool(row["enabled"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                tools=tools,
            )

    def check_connection(self, server_id: str) -> bool:
        """
        Checks connectivity of an MCP server by ID.
        """
        with get_connection() as db_conn:
            cursor = db_conn.cursor()
            cursor.execute("SELECT url, headers, timeout FROM mcp_servers WHERE id = ?", (server_id,))
            row = cursor.fetchone()
            if not row:
                return False

            headers = [HeaderItem(**h) for h in json.loads(row["headers"])]
            return self.check_connection_by_url(row["url"], headers, row["timeout"])

    def discover_tools(self, server_id: str) -> List[MCPToolDefinition]:
        """
        Discovers tools for a stored MCP server ID.
        """
        mcp_server = self.get_by_id(server_id)
        return mcp_server.tools if mcp_server else []

    def list_paginated(
        self,
        search: Optional[str] = None,
        page: int = 1,
        size: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> PaginatedMCPServersResponse:
        """
        Lists MCP servers with pagination, search, and sorting.
        """
        valid_sort_fields = {"name", "type", "url", "created_at", "updated_at"}
        field = sort_by if sort_by in valid_sort_fields else "created_at"
        order = "ASC" if sort_order.lower() == "asc" else "DESC"

        page = max(1, page)
        size = max(1, min(size, 100))
        offset = (page - 1) * size

        where_clause = ""
        params = []
        if search and search.strip():
            where_clause = "WHERE name LIKE ? OR url LIKE ?"
            term = f"%{search.strip()}%"
            params = [term, term]

        with get_connection() as db_conn:
            cursor = db_conn.cursor()

            cursor.execute(f"SELECT COUNT(*) as total FROM mcp_servers {where_clause}", params)
            total = cursor.fetchone()["total"]

            query_sql = f"""
                SELECT * FROM mcp_servers
                {where_clause}
                ORDER BY {field} {order}
                LIMIT ? OFFSET ?
            """
            cursor.execute(query_sql, params + [size, offset])
            rows = cursor.fetchall()

            items: List[MCPServerResponse] = []
            for row in rows:
                headers = [HeaderItem(**h) for h in json.loads(row["headers"])]
                tools = self.discover_tools_by_url(row["url"], headers, row["timeout"], server_id=row["id"], server_name=row["name"])
                items.append(
                    MCPServerResponse(
                        id=row["id"],
                        name=row["name"],
                        type=row["type"],
                        url=row["url"],
                        headers=headers,
                        timeout=row["timeout"],
                        enabled=bool(row["enabled"]),
                        created_at=row["created_at"],
                        updated_at=row["updated_at"],
                        tools=tools,
                    )
                )

            pages = math.ceil(total / size) if total > 0 else 0

            return PaginatedMCPServersResponse(
                items=items,
                total=total,
                page=page,
                size=size,
                pages=pages,
            )

    def get_all_ollama_tools(self) -> List[Dict[str, Any]]:
        """
        Gathers tools from all enabled MCP servers and formats them into the
        Ollama SDK tool calling specification payload (`tools=[{"type": "function", ...}]`).
        """
        ollama_tools: List[Dict[str, Any]] = []

        with get_connection() as db_conn:
            cursor = db_conn.cursor()
            cursor.execute("SELECT * FROM mcp_servers WHERE enabled = 1")
            rows = cursor.fetchall()

            for row in rows:
                headers = [HeaderItem(**h) for h in json.loads(row["headers"])]
                tools = self.discover_tools_by_url(row["url"], headers, row["timeout"], server_id=row["id"], server_name=row["name"])

                for t in tools:
                    ollama_tools.append(
                        {
                            "type": "function",
                            "function": {
                                "name": t.name,
                                "description": t.description or f"Tool provided by {t.server_name or 'MCP Server'}",
                                "parameters": t.parameters or {"type": "object", "properties": {}},
                            },
                        }
                    )

        return ollama_tools

    def execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> ToolExecutionResult:
        """
        Finds the MCP server associated with `tool_name` and sends the HTTP invocation request.
        Handles both REST POST requests and JSON-RPC 2.0 `tools/call`.
        """
        with get_connection() as db_conn:
            cursor = db_conn.cursor()
            cursor.execute("SELECT * FROM mcp_servers WHERE enabled = 1")
            rows = cursor.fetchall()

            target_server = None
            for row in rows:
                headers = [HeaderItem(**h) for h in json.loads(row["headers"])]
                tools = self.discover_tools_by_url(row["url"], headers, row["timeout"], server_id=row["id"], server_name=row["name"])
                if any(t.name == tool_name for t in tools):
                    target_server = row
                    break

            if not target_server:
                return ToolExecutionResult(
                    tool_name=tool_name,
                    success=False,
                    error=f"No enabled MCP server found that exposes tool '{tool_name}'",
                )

            headers = [HeaderItem(**h) for h in json.loads(target_server["headers"])]
            clean_url = self._normalize_url(target_server["url"])
            timeout = target_server["timeout"]

            try:
                res = self._send_http_request(
                    f"{clean_url}/tools/{tool_name}/execute",
                    method="POST",
                    headers=headers,
                    payload=arguments,
                    timeout=timeout,
                )
                return ToolExecutionResult(tool_name=tool_name, success=True, result=res)
            except Exception:
                pass

            try:
                rpc_payload = {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {"name": tool_name, "arguments": arguments},
                    "id": 1,
                }
                res = self._send_http_request(clean_url, method="POST", headers=headers, payload=rpc_payload, timeout=timeout)
                result_content = res.get("result") or res
                return ToolExecutionResult(tool_name=tool_name, success=True, result=result_content)
            except Exception as exc:
                logger.error(f"Failed to execute tool call '{tool_name}' on '{clean_url}': {exc}")
                return ToolExecutionResult(
                    tool_name=tool_name,
                    success=False,
                    error=f"Execution error on MCP server '{clean_url}': {exc}",
                )

