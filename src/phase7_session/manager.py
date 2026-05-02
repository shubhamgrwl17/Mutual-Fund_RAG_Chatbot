import sqlite3
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self, db_path: str = "data/sessions.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize SQLite tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    thread_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    scheme_id TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_thread ON messages(thread_id)")
            conn.commit()

    def save_message(self, thread_id: str, role: str, content: str, scheme_id: Optional[str] = None):
        """Save a message to the thread."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO messages (thread_id, role, content, scheme_id) VALUES (?, ?, ?, ?)",
                (thread_id, role, content, scheme_id)
            )
            conn.commit()

    def get_history(self, thread_id: str, limit: int = 6) -> List[Dict[str, str]]:
        """Retrieve recent messages for LLM context."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT role, content FROM messages WHERE thread_id = ? ORDER BY timestamp DESC LIMIT ?",
                (thread_id, limit)
            )
            # Reverse to get chronological order
            rows = cursor.fetchall()
            return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]

    def get_active_scheme(self, thread_id: str) -> Optional[str]:
        """Find the last mentioned scheme_id in the thread."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT scheme_id FROM messages WHERE thread_id = ? AND scheme_id IS NOT NULL ORDER BY timestamp DESC LIMIT 1",
                (thread_id,)
            )
            row = cursor.fetchone()
            return row[0] if row else None
