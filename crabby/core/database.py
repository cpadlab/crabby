import sqlite3
from pathlib import Path
from typing import Generator
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
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    """
    Initializes the SQLite database schema and creates necessary tables if they do not exist.
    """
    db_path = get_db_path()
    settings.CRABBY_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Initializing database at: {db_path}")

    with get_connection() as conn:
        
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
        conn.commit()

    logger.info("Database schema initialized successfully.")
