"""SQLite database setup and helpers."""

import sqlite3

from config import DATABASE_PATH


def get_connection():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables. Called on first use in later phases."""
    pass
