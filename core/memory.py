"""
Multi-Session Conversation Memory with Sliding Window and Auto-Summarization.
Preserves the last 20 messages per session while summarizing older conversation context.
"""

from datetime import datetime
import logging
from typing import Dict, List, Optional
import uuid

from core.config import AUTO_SUMMARIZE_THRESHOLD, MAX_HISTORY_MESSAGES

logger = logging.getLogger(__name__)


class Message:
    """Represents a single conversational turn."""

    def __init__(self, role: str, content: str, metadata: Optional[Dict] = None):
        self.role = role
        self.content = content
        self.timestamp = datetime.now().isoformat()
        self.metadata = metadata or {}

    def to_dict(self) -> Dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


class Session:
    """Maintains active message history, running summary, and session metadata."""

    def __init__(self, session_id: str, title: Optional[str] = None):
        self.session_id = session_id
        self.title = title or f"Session {session_id[:6]}"
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.messages: List[Message] = []
        self.summary: str = ""
        self.total_messages_count: int = 0

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        msg = Message(role=role, content=content, metadata=metadata)
        self.messages.append(msg)
        self.total_messages_count += 1
        self.updated_at = datetime.now().isoformat()

        # Update title from first user message
        if role == "user" and self.title.startswith("Session "):
            clean_title = content.strip()[:35]
            self.title = clean_title + ("..." if len(content) > 35 else "")

        # Auto-summarize older messages if exceeding window
        if len(self.messages) > AUTO_SUMMARIZE_THRESHOLD:
            self._summarize_and_truncate()

    def _summarize_and_truncate(self):
        """
        Compresses oldest messages beyond MAX_HISTORY_MESSAGES into session.summary
        and maintains the sliding window of the last 20 messages.
        """
        excess_count = len(self.messages) - MAX_HISTORY_MESSAGES
        if excess_count <= 0:
            return

        to_archive = self.messages[:excess_count]
        self.messages = self.messages[excess_count:]

        # Build running summary excerpt
        archive_excerpts = []
        for m in to_archive:
            tag = "User" if m.role == "user" else "Assistant"
            brief = m.content[:60] + ("..." if len(m.content) > 60 else "")
            archive_excerpts.append(f"{tag}: {brief}")

        new_notes = "; ".join(archive_excerpts)
        if self.summary:
            self.summary += f" | {new_notes}"
        else:
            self.summary = f"Earlier conversation topics: {new_notes}"

        logger.info(
            "Session %s pruned %d messages into summary (Active window: %d)",
            self.session_id, excess_count, len(self.messages)
        )

    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "active_messages_count": len(self.messages),
            "total_messages_count": self.total_messages_count,
            "has_summary": bool(self.summary),
            "summary": self.summary,
        }


class MemoryManager:
    """Manages multi-session lifecycle, retrieval, and persistence."""

    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        # Initialize default session
        self.default_session_id = "default_session"
        self.get_or_create_session(self.default_session_id, title="Main Conversation")

    def create_session(self, session_id: Optional[str] = None, title: Optional[str] = None) -> Session:
        sid = session_id or str(uuid.uuid4())[:8]
        session = Session(session_id=sid, title=title)
        self.sessions[sid] = session
        return session

    def get_or_create_session(self, session_id: Optional[str] = None, title: Optional[str] = None) -> Session:
        sid = session_id or self.default_session_id
        if sid not in self.sessions:
            return self.create_session(session_id=sid, title=title)
        return self.sessions[sid]

    def get_session(self, session_id: str) -> Optional[Session]:
        return self.sessions.get(session_id)

    def list_sessions(self) -> List[Dict]:
        """Lists metadata for all active sessions."""
        return [s.to_dict() for s in sorted(self.sessions.values(), key=lambda x: x.updated_at, reverse=True)]

    def delete_session(self, session_id: str) -> bool:
        if session_id in self.sessions:
            del self.sessions[session_id]
            # Ensure at least one default session exists
            if not self.sessions:
                self.create_session(self.default_session_id, title="Main Conversation")
            return True
        return False

    def get_history(self, session_id: str) -> List[Dict]:
        session = self.get_session(session_id)
        if not session:
            return []
        return [m.to_dict() for m in session.messages]


_MEMORY_INSTANCE = None


def get_memory_manager() -> MemoryManager:
    """Returns singleton MemoryManager."""
    global _MEMORY_INSTANCE
    if _MEMORY_INSTANCE is None:
        _MEMORY_INSTANCE = MemoryManager()
    return _MEMORY_INSTANCE
