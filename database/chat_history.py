import os
import re
import sqlite3
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# Default location: project_root/database/chat_history.db
DEFAULT_DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "chat_history.db")
)


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Creates a configured sqlite3 connection with Row factory and foreign keys enabled."""
    target_path = db_path or DEFAULT_DB_PATH
    db_dir = os.path.dirname(os.path.abspath(target_path))
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(target_path, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def initialize_database(db_path: Optional[str] = None) -> None:
    """Initializes the database schema if tables do not already exist."""
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    session_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_updated_at 
                ON conversations(updated_at DESC);
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                );
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_conversation_id 
                ON messages(conversation_id);
            """)
    finally:
        conn.close()


def create_conversation(
    title: Optional[str] = None,
    conversation_id: Optional[str] = None,
    session_id: Optional[str] = None,
    db_path: Optional[str] = None
) -> str:
    """Creates a new conversation record and returns the conversation_id."""
    initialize_database(db_path)
    conv_id = conversation_id or str(uuid.uuid4())
    conv_title = (title or "New Conversation").strip()
    now_iso = datetime.now(timezone.utc).isoformat()

    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO conversations (id, title, session_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (conv_id, conv_title, session_id, now_iso, now_iso)
            )
        return conv_id
    finally:
        conn.close()


def get_conversation(
    conversation_id: str,
    db_path: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Retrieves conversation metadata by ID."""
    if not conversation_id:
        return None
    initialize_database(db_path)
    conn = get_db_connection(db_path)
    try:
        cursor = conn.execute(
            """
            SELECT id, title, session_id, created_at, updated_at
            FROM conversations
            WHERE id = ?
            """,
            (conversation_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "title": row["title"],
            "session_id": row["session_id"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
    finally:
        conn.close()


def list_conversations(
    session_id: Optional[str] = None,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Lists conversations ordered by updated_at descending."""
    initialize_database(db_path)
    conn = get_db_connection(db_path)
    try:
        if session_id:
            cursor = conn.execute(
                """
                SELECT id, title, session_id, created_at, updated_at
                FROM conversations
                WHERE session_id = ?
                ORDER BY updated_at DESC, id DESC
                """,
                (session_id,)
            )
        else:
            cursor = conn.execute(
                """
                SELECT id, title, session_id, created_at, updated_at
                FROM conversations
                ORDER BY updated_at DESC, id DESC
                """
            )
        rows = cursor.fetchall()
        return [
            {
                "id": row["id"],
                "title": row["title"],
                "session_id": row["session_id"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }
            for row in rows
        ]
    finally:
        conn.close()


def delete_conversation(
    conversation_id: str,
    db_path: Optional[str] = None
) -> bool:
    """Deletes a conversation and cascaded messages."""
    if not conversation_id:
        return False
    initialize_database(db_path)
    conn = get_db_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                "DELETE FROM conversations WHERE id = ?",
                (conversation_id,)
            )
            return cursor.rowcount > 0
    finally:
        conn.close()


def update_conversation_title(
    conversation_id: str,
    title: str,
    db_path: Optional[str] = None
) -> bool:
    """Updates the conversation title."""
    if not conversation_id or not title:
        return False
    initialize_database(db_path)
    now_iso = datetime.now(timezone.utc).isoformat()
    conn = get_db_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                """
                UPDATE conversations
                SET title = ?, updated_at = ?
                WHERE id = ?
                """,
                (title.strip(), now_iso, conversation_id)
            )
            return cursor.rowcount > 0
    finally:
        conn.close()


def update_conversation_timestamp(
    conversation_id: str,
    db_path: Optional[str] = None
) -> bool:
    """Updates the updated_at timestamp of a conversation."""
    if not conversation_id:
        return False
    initialize_database(db_path)
    now_iso = datetime.now(timezone.utc).isoformat()
    conn = get_db_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                """
                UPDATE conversations
                SET updated_at = ?
                WHERE id = ?
                """,
                (now_iso, conversation_id)
            )
            return cursor.rowcount > 0
    finally:
        conn.close()


def save_message(
    conversation_id: str,
    role: str,
    content: str,
    db_path: Optional[str] = None
) -> int:
    """Saves a message into SQLite, validating role and updating conversation timestamp."""
    if not conversation_id:
        raise ValueError("conversation_id cannot be empty.")

    valid_roles = ("user", "assistant")
    if role not in valid_roles:
        raise ValueError(f"Invalid message role '{role}'. Allowed roles: {valid_roles}")

    if not isinstance(content, str) or not content.strip():
        raise ValueError("Message content cannot be empty.")

    initialize_database(db_path)
    now_iso = datetime.now(timezone.utc).isoformat()

    conn = get_db_connection(db_path)
    try:
        with conn:
            # Check conversation exists
            cur = conn.execute("SELECT id FROM conversations WHERE id = ?", (conversation_id,))
            if not cur.fetchone():
                raise ValueError(f"Conversation with id '{conversation_id}' does not exist.")

            # Insert message
            cursor = conn.execute(
                """
                INSERT INTO messages (conversation_id, role, content, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (conversation_id, role, content.strip(), now_iso)
            )
            msg_id = cursor.lastrowid

            # Update conversation timestamp
            conn.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (now_iso, conversation_id)
            )
            return msg_id
    finally:
        conn.close()


def get_messages(
    conversation_id: str,
    limit: Optional[int] = None,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Retrieves messages for a conversation in deterministic chronological order."""
    if not conversation_id:
        return []

    initialize_database(db_path)
    conn = get_db_connection(db_path)
    try:
        if limit is not None and limit > 0:
            cursor = conn.execute(
                """
                SELECT id, conversation_id, role, content, created_at
                FROM (
                    SELECT id, conversation_id, role, content, created_at
                    FROM messages
                    WHERE conversation_id = ?
                    ORDER BY created_at DESC, id DESC
                    LIMIT ?
                ) sub
                ORDER BY created_at ASC, id ASC
                """,
                (conversation_id, limit)
            )
        else:
            cursor = conn.execute(
                """
                SELECT id, conversation_id, role, content, created_at
                FROM messages
                WHERE conversation_id = ?
                ORDER BY created_at ASC, id ASC
                """,
                (conversation_id,)
            )
        rows = cursor.fetchall()
        return [
            {
                "id": row["id"],
                "conversation_id": row["conversation_id"],
                "role": row["role"],
                "content": row["content"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]
    finally:
        conn.close()


def generate_title_from_message(user_message: str, max_length: int = 40) -> str:
    """Generates a clean, concise, deterministic title from the first user question without calling Gemini."""
    if not user_message or not user_message.strip():
        return "New Conversation"

    clean_text = user_message.strip()

    # Remove leading common bot question patterns / filler
    clean_text = re.sub(
        r"^(what\s+is\s+the|what\s+are\s+the|what\s+is|what\s+are|how\s+can\s+i|how\s+do\s+we|how\s+to|can\s+you\s+explain|tell\s+me\s+about|why\s+is|what\s+about)\s+",
        "",
        clean_text,
        flags=re.IGNORECASE
    )

    # Clean up non-alphanumeric trailing characters
    clean_text = re.sub(r"[?!.,:;]+$", "", clean_text).strip()
    clean_text = re.sub(r"\s+", " ", clean_text)

    if not clean_text:
        clean_text = user_message.strip()

    # Truncate to max_length without splitting words if possible
    if len(clean_text) > max_length:
        truncated = clean_text[:max_length]
        last_space = truncated.rfind(" ")
        if last_space > 15:
            clean_text = truncated[:last_space]
        else:
            clean_text = truncated

    # Title-case for clean UI appearance
    words = clean_text.split()
    if words:
        clean_title = " ".join(w.capitalize() if not w.isupper() else w for w in words)
        return clean_title

    return "New Conversation"


class ChatHistoryDB:
    """Class wrapper providing object-oriented database access to SQLite chat history."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self.initialize()

    def initialize(self) -> None:
        initialize_database(self.db_path)

    def create_conversation(
        self,
        title: Optional[str] = None,
        conversation_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> str:
        return create_conversation(
            title=title,
            conversation_id=conversation_id,
            session_id=session_id,
            db_path=self.db_path
        )

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        return get_conversation(conversation_id, db_path=self.db_path)

    def list_conversations(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return list_conversations(session_id=session_id, db_path=self.db_path)

    def delete_conversation(self, conversation_id: str) -> bool:
        return delete_conversation(conversation_id, db_path=self.db_path)

    def update_conversation_title(self, conversation_id: str, title: str) -> bool:
        return update_conversation_title(conversation_id, title, db_path=self.db_path)

    def update_conversation_timestamp(self, conversation_id: str) -> bool:
        return update_conversation_timestamp(conversation_id, db_path=self.db_path)

    def save_message(self, conversation_id: str, role: str, content: str) -> int:
        return save_message(conversation_id, role, content, db_path=self.db_path)

    def get_messages(self, conversation_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return get_messages(conversation_id, limit=limit, db_path=self.db_path)

    def generate_title(self, user_message: str, max_length: int = 40) -> str:
        return generate_title_from_message(user_message, max_length=max_length)
