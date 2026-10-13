"""
Pydantic Schemas for Task 05 Chatbot API.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Payload for sending message to the chatbot."""
    message: str = Field(..., min_length=1, description="User input message or query")
    session_id: Optional[str] = Field(None, description="Optional conversation session ID")


class ToolResultPayload(BaseModel):
    """Execution output from a tool invocation."""
    success: bool
    result: str
    tool_name: str
    data: Optional[Any] = None


class ChatResponse(BaseModel):
    """Response returned by POST /api/chat."""
    session_id: str
    query: str
    response: str
    intent: str = Field(..., description="Classified intent: 'tool-use', 'question', 'command', 'chit-chat'")
    confidence: float = Field(..., description="Confidence score between 0.0 and 1.0")
    tool_used: Optional[str] = None
    tool_result: Optional[ToolResultPayload] = None
    has_memory_summary: bool
    session_summary: str
    timestamp: str


class CreateSessionRequest(BaseModel):
    """Request payload to create a new conversation session."""
    session_id: Optional[str] = None
    title: Optional[str] = None


class SessionMetadata(BaseModel):
    """Metadata describing a conversation session."""
    session_id: str
    title: str
    created_at: str
    updated_at: str
    active_messages_count: int
    total_messages_count: int
    has_summary: bool
    summary: str


class SessionListResponse(BaseModel):
    """Response returned by GET /api/session."""
    total_sessions: int
    sessions: List[SessionMetadata]


class HistoryItem(BaseModel):
    """Single message entry in history."""
    role: str
    content: str
    timestamp: str
    metadata: Dict = {}


class HistoryResponse(BaseModel):
    """Response returned by GET /api/session/{id}/history."""
    session_id: str
    title: str
    total_active_messages: int
    summary: str
    history: List[HistoryItem]


class DeleteSessionResponse(BaseModel):
    """Response returned by DELETE /api/session/{id}."""
    success: bool
    session_id: str
    message: str


class ToolMetadata(BaseModel):
    """Metadata describing an available tool."""
    name: str
    description: str


class ToolsListResponse(BaseModel):
    """Response returned by GET /api/tools."""
    tools: List[ToolMetadata]


class HealthResponse(BaseModel):
    """Health status response."""
    status: str
    version: str
    active_sessions: int
    available_tools: List[str]
