"""Database package for persistent storage."""
from database.chat_history import (
    ChatHistoryDB,
    initialize_database,
    create_conversation,
    get_conversation,
    list_conversations,
    delete_conversation,
    save_message,
    get_messages,
    update_conversation_timestamp,
    update_conversation_title,
    generate_title_from_message,
    DEFAULT_DB_PATH,
)

__all__ = [
    "ChatHistoryDB",
    "initialize_database",
    "create_conversation",
    "get_conversation",
    "list_conversations",
    "delete_conversation",
    "save_message",
    "get_messages",
    "update_conversation_timestamp",
    "update_conversation_title",
    "generate_title_from_message",
    "DEFAULT_DB_PATH",
]
