"""
Command history — SQLite-backed persistent storage for executed commands.
"""

import sqlite3
import datetime
import logging
from pathlib import Path
from omnishell.core import get_config_dir

logger = logging.getLogger(__name__)

DB_NAME = "history.db"


def _get_db_path() -> Path:
    return get_config_dir() / DB_NAME


def _get_connection():
    """Get a SQLite connection, creating the table if needed."""
    db_path = _get_db_path()
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            query TEXT NOT NULL,
            command TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'unknown',
            output TEXT DEFAULT '',
            mode TEXT DEFAULT 'pro',
            provider TEXT DEFAULT 'groq'
        )
    """)
    conn.commit()
    return conn


def save_command(
    query: str,
    command: str,
    status: str,
    output: str = "",
    mode: str = "pro",
    provider: str = "groq",
) -> None:
    """Save an executed command to history."""
    try:
        conn = _get_connection()
        conn.execute(
            """INSERT INTO history (timestamp, query, command, status, output, mode, provider)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                datetime.datetime.now().isoformat(),
                query,
                command,
                status,
                output[:5000],  # limit stored output size
                mode,
                provider,
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to save history: {e}")


def get_history(limit: int = 20) -> list[dict]:
    """
    Retrieve recent command history.

    Returns:
        List of dicts with keys: id, timestamp, query, command, status, mode, provider
    """
    try:
        conn = _get_connection()
        cursor = conn.execute(
            """SELECT id, timestamp, query, command, status, mode, provider
               FROM history ORDER BY id DESC LIMIT ?""",
            (limit,),
        )
        columns = ["id", "timestamp", "query", "command", "status", "mode", "provider"]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return results
    except Exception as e:
        logger.error(f"Failed to read history: {e}")
        return []


def clear_history() -> None:
    """Delete all command history."""
    try:
        conn = _get_connection()
        conn.execute("DELETE FROM history")
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to clear history: {e}")


def get_history_stats() -> dict:
    """Get summary statistics of command history."""
    try:
        conn = _get_connection()
        total = conn.execute("SELECT COUNT(*) FROM history").fetchone()[0]
        success = conn.execute("SELECT COUNT(*) FROM history WHERE status='success'").fetchone()[0]
        failed = conn.execute("SELECT COUNT(*) FROM history WHERE status='failed'").fetchone()[0]
        conn.close()
        return {"total": total, "success": success, "failed": failed}
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        return {"total": 0, "success": 0, "failed": 0}
