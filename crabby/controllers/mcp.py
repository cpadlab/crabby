import asyncio
import hashlib
import json
import math
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlsplit, urlunsplit

import httpx2
from mcp import Client
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamable_http_client

from crabby.core.database import get_connection
from crabby.core.secrets import decode_headers, encode_headers
from crabby.schemas.mcp import (
    HeaderItem,
    MCPServerCreate,
    MCPServerResponse,
    MCPServerUpdate,
    MCPHeaderResponse,
    MCPToolDefinition,
    PaginatedMCPServersResponse,
    ToolExecutionResult,
)
from crabby.shared.logger import logger


class MCPController:
    """Persistence and MCP protocol operations for configured remote servers."""

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _normalize_url(url: str) -> str:
        value = url.strip()
        if not value:
            raise ValueError("MCP server URL cannot be empty.")
        if "://" not in value:
            value = f"http://{value}"
        parsed = urlsplit(value)
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
            raise ValueError("MCP server URL must use HTTP or HTTPS and include a host.")
        if parsed.username or parsed.password:
            raise ValueError("Credentials must be configured as headers, not embedded in the URL.")
        if parsed.query or parsed.fragment:
            raise ValueError("MCP server URL cannot contain a query string or fragment.")
        try:
            parsed.port
        except ValueError as exc:
            raise ValueError("MCP server URL contains an invalid port.") from exc
        return urlunsplit((parsed.scheme.lower(), parsed.netloc, parsed.path.rstrip("/"), "", ""))

    @staticmethod
    def _headers_from_storage(value: str) -> tuple[List[HeaderItem], str | None]:
        return decode_headers(value, HeaderItem)

    @staticmethod
    def _public_headers(headers: List[HeaderItem]) -> List[MCPHeaderResponse]:
        return [MCPHeaderResponse(key=item.key, configured=bool(item.value)) for item in headers]

    @classmethod
    async def _request_tools(
        cls, url: str, transport_type: str, headers: List[HeaderItem], timeout: float,
        tool_name: Optional[str] = None, arguments: Optional[Dict[str, Any]] = None,
    ) -> Any:
        clean_url = cls._normalize_url(url)
        if transport_type not in {"http", "sse"}:
            raise ValueError("MCP transport must be 'http' or 'sse'.")
        timeout = min(max(float(timeout), 0.5), 300.0)
        request_headers = {item.key: item.value for item in headers if item.key and item.value}

        if transport_type == "sse":
            transport = sse_client(
                clean_url,
                headers=request_headers,
                timeout=timeout,
                sse_read_timeout=timeout,
            )
            async with Client(transport) as client:
                if tool_name is None:
                    return await client.list_tools()
                return await client.call_tool(tool_name, arguments or {})

        http_client = httpx2.AsyncClient(
            headers=request_headers,
            timeout=httpx2.Timeout(timeout, read=timeout),
        )
        async with http_client:
            transport = streamable_http_client(clean_url, http_client=http_client)
            async with Client(transport) as client:
                if tool_name is None:
                    return await client.list_tools()
                return await client.call_tool(tool_name, arguments or {})

    @classmethod
    def _run_protocol(cls, *args: Any, **kwargs: Any) -> Any:
        # PyWebView invokes this synchronous bridge outside an asyncio event loop.
        return asyncio.run(cls._request_tools(*args, **kwargs))

    @classmethod
    def check_connection_by_url(
        cls, url: str, headers: List[HeaderItem], timeout: float = 5.0, transport_type: str = "http"
    ) -> bool:
        try:
            cls._run_protocol(url, transport_type, headers, timeout)
            return True
        except Exception as exc:
            logger.debug("MCP connectivity check failed (%s).", type(exc).__name__)
            return False

    @classmethod
    def discover_tools_by_url(
        cls, url: str, headers: List[HeaderItem], timeout: float = 5.0,
        server_id: Optional[str] = None, server_name: Optional[str] = None,
        transport_type: str = "http",
    ) -> List[MCPToolDefinition]:
        result = cls._run_protocol(url, transport_type, headers, timeout)
        tools: List[MCPToolDefinition] = []
        for item in result.tools:
            schema = getattr(item, "input_schema", None) or getattr(item, "inputSchema", None) or {"type": "object", "properties": {}}
            if not isinstance(schema, dict):
                schema = {"type": "object", "properties": {}}
            tools.append(MCPToolDefinition(
                name=str(item.name), description=str(getattr(item, "description", "") or ""),
                input_schema=schema, parameters=schema, server_id=server_id, server_name=server_name,
            ))
        return tools

    @staticmethod
    def _read_cache(cursor: Any, server_id: str) -> List[MCPToolDefinition]:
        cursor.execute("SELECT tools FROM mcp_tool_cache WHERE server_id = ?", (server_id,))
        cache = cursor.fetchone()
        if not cache:
            return []
        try:
            return [MCPToolDefinition(**item) for item in json.loads(cache["tools"])]
        except (json.JSONDecodeError, TypeError, ValueError):
            return []

    @classmethod
    def _store_tools(cls, server_id: str, tools: List[MCPToolDefinition]) -> None:
        serialized = json.dumps([tool.model_dump() for tool in tools], ensure_ascii=False, separators=(",", ":"))
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO mcp_tool_cache (server_id, tools, synced_at) VALUES (?, ?, ?) "
                "ON CONFLICT(server_id) DO UPDATE SET tools = excluded.tools, synced_at = excluded.synced_at",
                (server_id, serialized, cls._now_iso()),
            )
            conn.commit()

    @classmethod
    def _server_response(cls, row: Any, tools: Optional[List[MCPToolDefinition]] = None) -> MCPServerResponse:
        headers, migrated = cls._headers_from_storage(row["headers"])
        if migrated:
            with get_connection() as conn:
                conn.execute("UPDATE mcp_servers SET headers = ? WHERE id = ?", (migrated, row["id"]))
                conn.commit()
        for tool in tools or []:
            tool.server_id = row["id"]
            tool.server_name = row["name"]
        return MCPServerResponse(
            id=row["id"], name=row["name"], type=row["type"], url=row["url"],
            headers=cls._public_headers(headers), timeout=row["timeout"], enabled=bool(row["enabled"]),
            created_at=row["created_at"], updated_at=row["updated_at"], tools=tools or [],
        )

    @classmethod
    def _load_server(cls, server_id: str) -> Any:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM mcp_servers WHERE id = ?", (server_id,)).fetchone()
        if row is None:
            raise KeyError("MCP server not found.")
        return row

    @classmethod
    def _refresh_row_tools(cls, row: Any) -> List[MCPToolDefinition]:
        headers, migrated = cls._headers_from_storage(row["headers"])
        if migrated:
            with get_connection() as conn:
                conn.execute("UPDATE mcp_servers SET headers = ? WHERE id = ?", (migrated, row["id"]))
                conn.commit()
        tools = cls.discover_tools_by_url(
            row["url"], headers, row["timeout"], server_id=row["id"],
            server_name=row["name"], transport_type=row["type"],
        )
        cls._store_tools(row["id"], tools)
        return tools

    def create(self, data: MCPServerCreate) -> MCPServerResponse:
        name = data.name.strip()
        url = self._normalize_url(data.url)
        server_id = f"mcp_{uuid.uuid4().hex[:12]}"
        now = self._now_iso()
        headers_json = encode_headers(data.headers)
        with get_connection() as conn:
            existing = conn.execute("SELECT 1 FROM mcp_servers WHERE name = ? COLLATE NOCASE", (name,)).fetchone()
            if existing:
                raise ValueError("An MCP server with this name already exists.")
            conn.execute(
                "INSERT INTO mcp_servers (id, name, type, url, headers, timeout, enabled, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (server_id, name, data.type, url, headers_json, data.timeout, int(data.enabled), now, now),
            )
            conn.commit()
        logger.info("Registered MCP server %s.", server_id)
        # Registration remains available while a server is temporarily offline.
        try:
            tools = self.discover_tools_by_url(url, data.headers, data.timeout, server_id, name, data.type)
            self._store_tools(server_id, tools)
        except Exception as exc:
            logger.info("MCP tool discovery deferred for %s (%s).", server_id, type(exc).__name__)
            tools = []
        row = self._load_server(server_id)
        return self._server_response(row, tools)

    def update(self, server_id: str, data: MCPServerUpdate) -> MCPServerResponse:
        row = self._load_server(server_id)
        existing_headers, migrated = self._headers_from_storage(row["headers"])
        name = data.name if data.name is not None else row["name"]
        url = self._normalize_url(data.url) if data.url is not None else row["url"]
        transport = data.type or row["type"]
        timeout = data.timeout if data.timeout is not None else row["timeout"]
        enabled = data.enabled if data.enabled is not None else bool(row["enabled"])
        if name.casefold() != row["name"].casefold():
            with get_connection() as conn:
                duplicate = conn.execute(
                    "SELECT 1 FROM mcp_servers WHERE name = ? COLLATE NOCASE AND id != ?", (name, server_id)
                ).fetchone()
            if duplicate:
                raise ValueError("An MCP server with this name already exists.")

        headers = existing_headers
        if data.headers is not None:
            previous = {item.key.casefold(): item.value for item in existing_headers}
            headers = []
            for item in data.headers:
                value = item.value
                if not value and item.configured:
                    value = previous.get(item.key.casefold(), "")
                    if not value:
                        raise ValueError(f"A value is required for the new header '{item.key}'.")
                headers.append(HeaderItem(key=item.key, value=value))
        headers_json = encode_headers(headers) if data.headers is not None or migrated else row["headers"]
        now = self._now_iso()
        with get_connection() as conn:
            conn.execute(
                "UPDATE mcp_servers SET name = ?, type = ?, url = ?, headers = ?, timeout = ?, enabled = ?, updated_at = ? WHERE id = ?",
                (name, transport, url, headers_json, timeout, int(enabled), now, server_id),
            )
            conn.commit()

        changed_connection = (url != row["url"] or transport != row["type"] or headers_json != row["headers"])
        if changed_connection:
            with get_connection() as conn:
                conn.execute("DELETE FROM mcp_tool_cache WHERE server_id = ?", (server_id,))
                conn.commit()
        updated = self._load_server(server_id)
        try:
            tools = self._refresh_row_tools(updated) if changed_connection else self._read_tools(server_id)
        except Exception as exc:
            logger.info("MCP tool refresh deferred for %s (%s).", server_id, type(exc).__name__)
            tools = self._read_tools(server_id)
        return self._server_response(updated, tools)

    @staticmethod
    def _read_tools(server_id: str) -> List[MCPToolDefinition]:
        with get_connection() as conn:
            return MCPController._read_cache(conn.cursor(), server_id)

    def delete(self, server_id: str) -> bool:
        with get_connection() as conn:
            cursor = conn.execute("DELETE FROM mcp_servers WHERE id = ?", (server_id,))
            conn.commit()
            if cursor.rowcount == 0:
                raise KeyError("MCP server not found.")
        logger.info("Deleted MCP server %s.", server_id)
        return True

    def get_by_id(self, server_id: str) -> Optional[MCPServerResponse]:
        try:
            row = self._load_server(server_id)
        except KeyError:
            return None
        return self._server_response(row, self._read_tools(server_id))

    def check_connection(self, server_id: str) -> bool:
        row = self._load_server(server_id)
        headers, migrated = self._headers_from_storage(row["headers"])
        if migrated:
            with get_connection() as conn:
                conn.execute("UPDATE mcp_servers SET headers = ? WHERE id = ?", (migrated, server_id))
                conn.commit()
        return self.check_connection_by_url(row["url"], headers, row["timeout"], row["type"])

    def discover_tools(self, server_id: str) -> List[MCPToolDefinition]:
        row = self._load_server(server_id)
        return self._refresh_row_tools(row)

    def list_paginated(
        self, search: Optional[str] = None, page: int = 1, size: int = 10,
        sort_by: str = "created_at", sort_order: str = "desc",
    ) -> PaginatedMCPServersResponse:
        valid_fields = {"name", "type", "url", "created_at", "updated_at"}
        field = sort_by if sort_by in valid_fields else "created_at"
        order = "ASC" if sort_order.lower() == "asc" else "DESC"
        page = max(1, page)
        size = max(1, min(size, 100))
        params: List[Any] = []
        where = ""
        if search and search.strip():
            where = "WHERE name LIKE ? OR url LIKE ?"
            term = f"%{search.strip()}%"
            params = [term, term]
        with get_connection() as conn:
            total = conn.execute(f"SELECT COUNT(*) AS total FROM mcp_servers {where}", params).fetchone()["total"]
            rows = conn.execute(
                f"SELECT * FROM mcp_servers {where} ORDER BY {field} {order} LIMIT ? OFFSET ?",
                params + [size, (page - 1) * size],
            ).fetchall()
            items = [self._server_response(row, self._read_cache(conn.cursor(), row["id"])) for row in rows]
        return PaginatedMCPServersResponse(
            items=items, total=total, page=page, size=size, pages=math.ceil(total / size) if total else 0,
        )

    @staticmethod
    def _ollama_tool_name(server_id: str, tool_name: str) -> str:
        suffix = hashlib.sha256(tool_name.encode("utf-8")).hexdigest()[:12]
        return f"mcp_{server_id.removeprefix('mcp_')}__{suffix}"

    def get_all_ollama_tools(self) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            rows = conn.execute("SELECT * FROM mcp_servers WHERE enabled = 1").fetchall()
            results = []
            for row in rows:
                for tool in self._read_cache(conn.cursor(), row["id"]):
                    results.append({"type": "function", "function": {
                        "name": self._ollama_tool_name(row["id"], tool.name),
                        "description": tool.description or f"Tool from {row['name']} (original name: {tool.name})",
                        "parameters": tool.input_schema or tool.parameters or {"type": "object", "properties": {}},
                    }})
        return results

    def execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> ToolExecutionResult:
        if not isinstance(arguments, dict):
            return ToolExecutionResult(tool_name=tool_name, success=False, error="Tool arguments must be an object.")
        with get_connection() as conn:
            rows = conn.execute("SELECT * FROM mcp_servers WHERE enabled = 1").fetchall()
            candidates = []
            for row in rows:
                for cached in self._read_cache(conn.cursor(), row["id"]):
                    if self._ollama_tool_name(row["id"], cached.name) == tool_name:
                        candidates.append((row, cached.name))
                    elif cached.name == tool_name:
                        candidates.append((row, cached.name))
        if len(candidates) != 1:
            reason = "No enabled MCP server exposes this tool." if not candidates else "This tool name is ambiguous across MCP servers."
            return ToolExecutionResult(tool_name=tool_name, success=False, error=reason)
        row, original_name = candidates[0]
        headers, migrated = self._headers_from_storage(row["headers"])
        if migrated:
            with get_connection() as conn:
                conn.execute("UPDATE mcp_servers SET headers = ? WHERE id = ?", (migrated, row["id"]))
                conn.commit()
        try:
            result = self._run_protocol(row["url"], row["type"], headers, row["timeout"], original_name, arguments)
            payload = result.model_dump(mode="json") if hasattr(result, "model_dump") else result
            if getattr(result, "is_error", False):
                return ToolExecutionResult(tool_name=tool_name, success=False, result=payload, error="The MCP server reported a tool execution error.")
            return ToolExecutionResult(tool_name=tool_name, success=True, result=payload)
        except Exception as exc:
            logger.warning("MCP tool call failed for server %s (%s).", row["id"], type(exc).__name__)
            return ToolExecutionResult(tool_name=tool_name, success=False, error="MCP tool execution failed. Check the server connection and tool arguments.")
