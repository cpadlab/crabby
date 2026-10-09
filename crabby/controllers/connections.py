import json
import math
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit
from typing import Dict, List, Optional

from ollama import Client

from crabby.core.database import get_connection
from crabby.core.secrets import decode_headers, encode_headers
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
        clean = host.strip()
        if not clean:
            raise ValueError("Connection host URL cannot be empty.")
        if "://" not in clean:
            clean = f"http://{clean}"
        parsed = urlsplit(clean)
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
            raise ValueError("Connection host must be a valid HTTP or HTTPS URL.")
        if parsed.username or parsed.password:
            raise ValueError("Credentials must be configured as headers, not embedded in the URL.")
        if parsed.query or parsed.fragment:
            raise ValueError("Connection host cannot contain a query string or fragment.")
        try:
            parsed.port
        except ValueError as exc:
            raise ValueError("Connection host contains an invalid port.") from exc
        return urlunsplit((parsed.scheme.lower(), parsed.netloc, parsed.path.rstrip("/"), "", ""))

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
        except Exception:
            logger.warning("Could not fetch models from configured Ollama host.")
            return []

    @classmethod
    def check_connection_by_url(cls, host: str, headers: List[HeaderItem], timeout: float = 5.0) -> bool:
        """
        Tests if an Ollama server is online and reachable using official Ollama SDK.
        """
        try:
            client = cls._get_ollama_client(host, headers, timeout=min(max(timeout, 0.5), 10.0))
            client.list()
            return True
        except Exception:
            logger.debug("Ollama health check failed for configured host.")
            return False

    def create(self, data: ConnectionCreate) -> ConnectionResponse:
        """
        Creates a new connection record with input validation and name uniqueness.
        """
        if not data.name or not data.name.strip():
            raise ValueError("Connection name cannot be empty.")
        if not data.host or not data.host.strip():
            raise ValueError("Connection host URL cannot be empty.")
        if not 0.5 <= data.timeout <= 300:
            raise ValueError("Connection timeout must be between 0.5 and 300 seconds.")

        data.host = self._normalize_host(data.host)

        if not self.check_connection_by_url(data.host, data.headers, min(data.timeout, 10.0)):
            raise ValueError(f"Unable to connect to the server at '{data.host}'. Check the URL and network permissions.")

        now = self._now_iso()
        conn_id = f"conn_{uuid.uuid4().hex[:12]}"
        headers_json = encode_headers(data.headers)

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
            if data.timeout is not None and not 0.5 <= data.timeout <= 300:
                raise ValueError("Connection timeout must be between 0.5 and 300 seconds.")
            new_timeout = data.timeout if data.timeout is not None else row["timeout"]

            if data.headers is not None:
                new_headers = data.headers
                keys = [header.key.casefold() for header in data.headers]
                if len(keys) != len(set(keys)):
                    raise ValueError("Header names must be unique.")
                new_headers = data.headers
                headers_json = encode_headers(data.headers)
            else:
                headers_raw = row["headers"]
                new_headers, migrated = decode_headers(headers_raw)
                headers_json = migrated or headers_raw

            if not self.check_connection_by_url(new_host, new_headers, min(new_timeout, 10.0)):
                raise ValueError(f"Unable to connect to the server at '{new_host}'. Check the URL and network permissions.")

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

            headers, migrated = decode_headers(row["headers"])
            if migrated:
                db_conn.execute("UPDATE connections SET headers = ? WHERE id = ?", (migrated, conn_id))
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

            headers, migrated = decode_headers(row["headers"])
            if migrated:
                db_conn.execute("UPDATE connections SET headers = ? WHERE id = ?", (migrated, conn_id))
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
        with ThreadPoolExecutor(max_workers=min(4, max(1, len(rows)))) as pool:
            decoded = list(pool.map(lambda r: decode_headers(r["headers"]), rows))
            models_by_index = list(pool.map(
                lambda pair: self._fetch_ollama_models(pair[0]["host"], pair[1][0], timeout=min(2.0, pair[0]["timeout"])),
                zip(rows, decoded),
            ))
        for r, (headers, migrated), models in zip(rows, decoded, models_by_index):
            if migrated:
                with get_connection() as db_conn:
                    db_conn.execute("UPDATE connections SET headers = ? WHERE id = ?", (migrated, r["id"]))
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
