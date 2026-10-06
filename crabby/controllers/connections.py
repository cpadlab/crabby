import json
import math
import uuid
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import List, Optional

from crabby.core.database import get_connection
from crabby.schemas.connections import (
    ConnectionCreate,
    ConnectionResponse,
    ConnectionUpdate,
    HeaderItem,
    PaginatedConnectionsResponse,
)
from crabby.shared.logger import logger


class ConnectionController:
    """
    Controller for managing model connection providers (e.g., Ollama).
    """

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _fetch_ollama_models(host: str, headers: List[HeaderItem], timeout: float = 5.0) -> List[str]:
        """
        Fetches available model names from an Ollama host (/api/tags).
        """
        url = host.rstrip("/") + "/api/tags"
        req_headers = {"User-Agent": "Crabby-Desktop-App"}
        for item in headers:
            req_headers[item.key] = item.value

        try:
            req = urllib.request.Request(url, headers=req_headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    payload = json.loads(response.read().decode("utf-8"))
                    raw_models = payload.get("models", [])
                    return [m.get("name") for m in raw_models if m.get("name")]
        except Exception as exc:
            logger.debug(f"Failed to fetch models from {url}: {exc}")

        return []


    @staticmethod
    def check_connection_by_url(host: str, headers: List[HeaderItem], timeout: float = 5.0) -> bool:
        """
        Tests if an Ollama host is reachable.
        """
        url = host.rstrip("/") + "/api/version"
        req_headers = {"User-Agent": "Crabby-Desktop-App"}
        for item in headers:
            req_headers[item.key] = item.value

        try:
            req = urllib.request.Request(url, headers=req_headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.status in (200, 204)
        except Exception:
            try:
                fallback_url = host.rstrip("/") + "/api/tags"
                fallback_req = urllib.request.Request(fallback_url, headers=req_headers)
                with urllib.request.urlopen(fallback_req, timeout=timeout) as resp:
                    return resp.status in (200, 204)
            except Exception:
                return False


    def create(self, data: ConnectionCreate) -> ConnectionResponse:
        """
        Creates a new connection record, ensuring name uniqueness.
        """
        now = self._now_iso()
        conn_id = f"conn_{uuid.uuid4().hex[:12]}"
        headers_json = json.dumps([h.model_dump() for h in data.headers])

        with get_connection() as db_conn:
            cursor = db_conn.cursor()
            
            cursor.execute("SELECT id FROM connections WHERE name = ?", (data.name,))
            if cursor.fetchone():
                raise ValueError(f"A connection with the name '{data.name}' already exists.")

            cursor.execute(
                """
                INSERT INTO connections (id, name, type, host, headers, timeout, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (conn_id, data.name, data.type, data.host, headers_json, data.timeout, now, now),
            )
            db_conn.commit()

        models = self._fetch_ollama_models(data.host, data.headers, data.timeout)

        return ConnectionResponse(
            id=conn_id,
            name=data.name,
            type=data.type,
            host=data.host,
            headers=data.headers,
            timeout=data.timeout,
            created_at=now,
            updated_at=now,
            models=models,
        )


    def update(self, conn_id: str, data: ConnectionUpdate) -> ConnectionResponse:
        """
        Updates an existing connection by ID.
        """
        now = self._now_iso()

        with get_connection() as db_conn:
            cursor = db_conn.cursor()
            cursor.execute("SELECT * FROM connections WHERE id = ?", (conn_id,))
            row = cursor.fetchone()
            if not row:
                raise KeyError(f"Connection with ID '{conn_id}' not found.")

            current_name = row["name"]
            new_name = data.name if data.name is not None else current_name
            
            if data.name is not None and data.name != current_name:
                cursor.execute("SELECT id FROM connections WHERE name = ? AND id != ?", (data.name, conn_id))
                if cursor.fetchone():
                    raise ValueError(f"A connection with the name '{data.name}' already exists.")

            new_host = data.host if data.host is not None else row["host"]
            new_timeout = data.timeout if data.timeout is not None else row["timeout"]

            if data.headers is not None:
                new_headers = data.headers
                headers_json = json.dumps([h.model_dump() for h in data.headers])
            else:
                headers_raw = row["headers"]
                new_headers = [HeaderItem(**item) for item in json.loads(headers_raw)]
                headers_json = headers_raw

            cursor.execute(
                """
                UPDATE connections
                SET name = ?, host = ?, headers = ?, timeout = ?, updated_at = ?
                WHERE id = ?
                """,
                (new_name, new_host, headers_json, new_timeout, now, conn_id),
            )
            db_conn.commit()
            created_at = row["created_at"]
            conn_type = row["type"]

        models = self._fetch_ollama_models(new_host, new_headers, new_timeout)

        return ConnectionResponse(
            id=conn_id,
            name=new_name,
            type=conn_type,
            host=new_host,
            headers=new_headers,
            timeout=new_timeout,
            created_at=created_at,
            updated_at=now,
            models=models,
        )


    def delete(self, conn_id: str) -> bool:
        """
        Deletes a connection record by ID.
        """
        with get_connection() as db_conn:
            cursor = db_conn.cursor()
            cursor.execute("DELETE FROM connections WHERE id = ?", (conn_id,))
            db_conn.commit()
            return cursor.rowcount > 0


    def check_connection(self, conn_id: str) -> bool:
        """
        Checks connectivity for an existing connection by ID.
        """
        with get_connection() as db_conn:
            cursor = db_conn.cursor()
            cursor.execute("SELECT host, headers, timeout FROM connections WHERE id = ?", (conn_id,))
            row = cursor.fetchone()
            if not row:
                return False

            headers = [HeaderItem(**h) for h in json.loads(row["headers"])]
            return self.check_connection_by_url(row["host"], headers, row["timeout"])


    def get_models(self, conn_id: str) -> List[str]:
        """
        Retrieves list of available models for a connection by ID.
        """
        with get_connection() as db_conn:
            cursor = db_conn.cursor()
            cursor.execute("SELECT host, headers, timeout FROM connections WHERE id = ?", (conn_id,))
            row = cursor.fetchone()
            if not row:
                return []

            headers = [HeaderItem(**h) for h in json.loads(row["headers"])]
            return self._fetch_ollama_models(row["host"], headers, row["timeout"])


    def list_paginated(
        self,
        search: Optional[str] = None,
        page: int = 1,
        size: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> PaginatedConnectionsResponse:
        """
        Lists connections with pagination, search, and sorting.
        """
        valid_sort_fields = {"name", "type", "host", "created_at", "updated_at"}
        field = sort_by if sort_by in valid_sort_fields else "created_at"
        order = "ASC" if sort_order.lower() == "asc" else "DESC"

        offset = max(0, (page - 1) * size)

        where_clause = ""
        params = []
        if search and search.strip():
            where_clause = "WHERE name LIKE ? OR host LIKE ?"
            term = f"%{search.strip()}%"
            params = [term, term]

        with get_connection() as db_conn:
            cursor = db_conn.cursor()
            
            count_sql = f"SELECT COUNT(*) as total FROM connections {where_clause}"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()["total"]

            query_sql = f"""
                SELECT * FROM connections
                {where_clause}
                ORDER BY {field} {order}
                LIMIT ? OFFSET ?
            """
            cursor.execute(query_sql, params + [size, offset])
            rows = cursor.fetchall()

        items = []
        for r in rows:
            headers = [HeaderItem(**h) for h in json.loads(r["headers"])]
            models = self._fetch_ollama_models(r["host"], headers, timeout=2.0)
            items.append(
                ConnectionResponse(
                    id=r["id"],
                    name=r["name"],
                    type=r["type"],
                    host=r["host"],
                    headers=headers,
                    timeout=r["timeout"],
                    created_at=r["created_at"],
                    updated_at=r["updated_at"],
                    models=models,
                )
            )

        pages = math.ceil(total / size) if size > 0 else 0

        return PaginatedConnectionsResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages,
        )
