import sqlite3
import os
import platform
from pathlib import Path

from crabby.core.config import settings
from crabby.shared.logger import logger


def get_db_path() -> Path:
    """
    Returns the absolute path to the local SQLite database file.
    """
    return settings.CRABBY_DIR / "database.db"


def get_connection() -> sqlite3.Connection:
    """
    Creates and returns a sqlite3 Connection instance configured for WAL mode and dict-like rows.
    """
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path), timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA busy_timeout = 15000;")
    return conn


def init_db() -> None:
    """
    Initializes the SQLite database schema and creates necessary tables if they do not exist.
    """
    db_path = get_db_path()
    settings.CRABBY_DIR.mkdir(parents=True, exist_ok=True)
    if platform.system().lower() == "darwin":
        os.chmod(settings.CRABBY_DIR, 0o700)
    logger.info(f"Initializing database at: {db_path}")

    with get_connection() as conn:
        conn.execute("PRAGMA journal_mode = WAL;")
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS connections (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                type TEXT NOT NULL DEFAULT 'ollama',
                host TEXT NOT NULL,
                headers TEXT NOT NULL DEFAULT '[]',
                timeout REAL NOT NULL DEFAULT 30.0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS mcp_servers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                type TEXT NOT NULL DEFAULT 'http',
                url TEXT NOT NULL,
                headers TEXT NOT NULL DEFAULT '[]',
                timeout REAL NOT NULL DEFAULT 30.0,
                enabled INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS mcp_tool_cache (
                server_id TEXT PRIMARY KEY REFERENCES mcp_servers(id) ON DELETE CASCADE,
                tools TEXT NOT NULL DEFAULT '[]',
                synced_at TEXT NOT NULL
            );
            """
        )

        conn.commit()

    if platform.system().lower() == "darwin":
        os.chmod(db_path, 0o600)

    logger.info("Database schema initialized successfully.")
