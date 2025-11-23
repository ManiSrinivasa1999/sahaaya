"""
Simple SQLite cache for API responses.
Provides: init_cache_db, cache_response, get_cached_response

This module is intentionally small and dependency-free so it works in
offline/testing environments. Keys are opaque strings (e.g. hashes of
queries) and responses are stored as JSON text.
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, Dict

DB_PATH_DEFAULT = os.path.join(os.path.dirname(__file__), "..", "sahaaya_cache.db")


def _get_conn(db_path: str):
    return sqlite3.connect(db_path)


def init_cache_db(db_path: Optional[str] = None):
    """Initialize the cache database and tables."""
    if not db_path:
        db_path = os.path.abspath(DB_PATH_DEFAULT)

    conn = _get_conn(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS api_cache (
                key TEXT PRIMARY KEY,
                response_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def cache_response(key: str, response: Dict, db_path: Optional[str] = None) -> None:
    """Store a response dict in the cache under `key`. Overwrites existing entry."""
    if not db_path:
        db_path = os.path.abspath(DB_PATH_DEFAULT)

    conn = _get_conn(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO api_cache (key, response_json, created_at) VALUES (?, ?, ?)",
            (key, json.dumps(response, ensure_ascii=False), datetime.utcnow()),
        )
        conn.commit()
    finally:
        conn.close()


def get_cached_response(key: str, db_path: Optional[str] = None) -> Optional[Dict]:
    """Retrieve a cached response by key. Returns None if not found."""
    if not db_path:
        db_path = os.path.abspath(DB_PATH_DEFAULT)

    if not os.path.exists(db_path):
        return None

    conn = _get_conn(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT response_json FROM api_cache WHERE key = ?", (key,))
        row = cur.fetchone()
        if not row:
            return None
        try:
            return json.loads(row[0])
        except Exception:
            return None
    finally:
        conn.close()
