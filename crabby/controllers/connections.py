import json
import math
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

import ollama
from ollama import Client, ResponseError

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
    Robust controller for managing model connection providers (Ollama, etc.)
    using the official Ollama Python SDK.
    """

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _normalize_host(host: str) -> str:
        clean = host.strip().rstrip("/")
        if not clean.startswith(("http://", "https://")):
            clean = f"http://{clean}"
        return clean

    @classmethod
    def _get_ollama_client(cls, host: str, headers: List[HeaderItem], timeout: float = 5.0) -> Client:
        clean_host = cls._normalize_host(host)
        header_dict: Dict[str, str] = {item.key: item.value for item in headers if item.key and item.value}
        return Client(host=clean_host, headers=header_dict, timeout=timeout)

    @classmethod
    def _fetch_ollama_models(cls, host: str, headers: List[HeaderItem], timeout: float = 5.0) -> List[str]:
        """
        Fetches available model names using official Ollama Python SDK.
        """
        try:
            client = cls._get_ollama_client(host, headers, timeout=timeout)
            response = client.list()
            model_names: List[str] = []
            
            models_list = getattr(response, "models", [])
            for m in models_list:
                name = getattr(m, "model", None) or getattr(m, "name", None)
                if name:
                    model_names.append(name)

            return model_names
        except Exception as exc:
            logger.warning(f"Could not fetch models from Ollama host '{host}': {exc}")
            return []

    @classmethod
    def check_connection_by_url(cls, host: str, headers: List[HeaderItem], timeout: float = 5.0) -> bool:
        """
        Tests if an Ollama server is online and reachable using official Ollama SDK.
        """
        try:
            client = cls._get_ollama_client(host, headers, timeout=timeout)
            client.list()
            return True
        except (ResponseError, Exception) as exc:
            logger.debug(f"Health check failed for Ollama host '{host}': {exc}")
            return False

    def create(self, data: ConnectionCreate) -> ConnectionResponse:
        """
        Creates a new connection record with input validation and name uniqueness.
        """
        if not data.name or not data.name.strip():
            raise ValueError("Connection name cannot be empty.")
        if not data.host or not data.host.strip():
            raise ValueError("Connection host URL cannot be empty.")
        if data.timeout <= 0:
            raise ValueError("Connection timeout must be a positive number.")

        data.host = self._normalize_host(data.host)

        if not self.check_connection_by_url(data.host, data.headers, data.timeout):
            raise ValueError(f"Unable to connect to the server at '{data.host}'. Check the URL and network permissions.")

        now = self._now_iso()
        conn_id = f"conn_{uuid.uuid4().hex[:12]}"
        headers_json = json.dumps([h.model_dump() for h in data.headers])

        with get_connection() as db_conn:
            cursor = db_conn.cursor()
            
            cursor.execute("SELECT id FROM connections WHERE LOWER(name) = LOWER(?)", (data.name.strip(),))
            if cursor.fetchone():
                raise ValueError(f"A connection with the name '{data.name.strip()}' already exists.")

            cursor.execute(
                """
                INSERT INTO connections (id, name, type, host, headers, timeout, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (conn_id, data.name.strip(), data.type, data.host, headers_json, data.timeout, now, now),
            )
            db_conn.commit()

        logger.info(f"Created new connection '{data.name}' (ID: {conn_id})")
        models = self._fetch_ollama_models(data.host, data.headers, data.timeout)

        return ConnectionResponse(
            id=conn_id,
            name=data.name.strip(),
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
        Updates an existing connection by ID with validation.
        """
        now = self._now_iso()

        with get_connection() as db_conn:
            cursor = db_conn.cursor()
            cursor.execute("SELECT * FROM connections WHERE id = ?", (conn_id,))
            row = cursor.fetchone()
            if not row:
                raise KeyError(f"Connection with ID '{conn_id}' not found.")

            current_name = row["name"]
            new_name = data.name.strip() if data.name and data.name.strip() else current_name
            
            if data.name is not None and new_name.lower() != current_name.lower():
                cursor.execute("SELECT id FROM connections WHERE LOWER(name) = LOWER(?) AND id != ?", (new_name, conn_id))
                if cursor.fetchone():
                    raise ValueError(f"A connection with the name '{new_name}' already exists.")

            new_host = self._normalize_host(data.host) if data.host and data.host.strip() else row["host"]
            new_timeout = data.timeout if data.timeout is not None and data.timeout > 0 else row["timeout"]

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

        logger.info(f"Updated connection '{new_name}' (ID: {conn_id})")
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
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Deleted connection with ID: {conn_id}")
            return deleted

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

        page = max(1, page)
        size = max(1, min(size, 100))
        offset = (page - 1) * size

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
