"""
FastAPI Routes for Task 05 Chatbot API.
Provides endpoints for chat execution, session management, history inspection, and tool discovery.
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, status

from api.schemas import (
    ChatRequest,
    ChatResponse,
    CreateSessionRequest,
    DeleteSessionResponse,
    HealthResponse,
    HistoryResponse,
    SessionListResponse,
    SessionMetadata,
    ToolMetadata,
    ToolsListResponse,
)
from core.bot import get_chatbot_engine
from core.config import API_VERSION
from core.memory import get_memory_manager
from core.tools import get_tool_registry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Chatbot"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health & Readiness Check",
    description="Returns chatbot operational health, active session count, and registered tools.",
)
async def health_check() -> HealthResponse:
    mem = get_memory_manager()
    tools = get_tool_registry().list_tools()
    return HealthResponse(
        status="healthy",
        version=API_VERSION,
        active_sessions=len(mem.sessions),
        available_tools=[t["name"] for t in tools],
    )


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Send Chat Message & Get Tool-Augmented Response",
    description="Processes user message with session memory, classifies intent, runs tool if needed, and replies.",
)
async def chat(request: ChatRequest) -> ChatResponse:
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="User message cannot be empty.")

    bot = get_chatbot_engine()
    try:
        result = bot.process_message(query=request.message, session_id=request.session_id)
        return ChatResponse(**result)
    except Exception as e:
        logger.exception("Error processing chat: %s", e)
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@router.post(
    "/session/new",
    response_model=SessionMetadata,
    summary="Create New Conversation Session",
    description="Initializes a new isolated conversation session with its own sliding memory window.",
)
async def create_new_session(request: Optional[CreateSessionRequest] = None) -> SessionMetadata:
    mem = get_memory_manager()
    sid = request.session_id if request else None
    title = request.title if request else None
    session = mem.create_session(session_id=sid, title=title)
    return SessionMetadata(**session.to_dict())


@router.get(
    "/session",
    response_model=SessionListResponse,
    summary="List All Conversation Sessions",
    description="Returns metadata, active message counts, and summary flags for all sessions.",
)
async def list_sessions() -> SessionListResponse:
    mem = get_memory_manager()
    sessions = mem.list_sessions()
    return SessionListResponse(
        total_sessions=len(sessions),
        sessions=[SessionMetadata(**s) for s in sessions],
    )


@router.get(
    "/session/{session_id}/history",
    response_model=HistoryResponse,
    summary="Retrieve Session Conversation History",
    description="Fetches recent message history (sliding window up to 20 messages) and archived summary.",
)
async def get_session_history(session_id: str) -> HistoryResponse:
    mem = get_memory_manager()
    session = mem.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    history = [m.to_dict() for m in session.messages]
    return HistoryResponse(
        session_id=session.session_id,
        title=session.title,
        total_active_messages=len(history),
        summary=session.summary,
        history=history,
    )


@router.delete(
    "/session/{session_id}",
    response_model=DeleteSessionResponse,
    summary="Delete Conversation Session",
    description="Removes a session and all associated memory.",
)
async def delete_session(session_id: str) -> DeleteSessionResponse:
    mem = get_memory_manager()
    deleted = mem.delete_session(session_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    return DeleteSessionResponse(
        success=True,
        session_id=session_id,
        message=f"Session '{session_id}' deleted successfully.",
    )


@router.get(
    "/tools",
    response_model=ToolsListResponse,
    summary="List Registered Tools",
    description="Returns descriptions of all available tools: Calculator, Weather, Dictionary, Wikipedia.",
)
async def list_available_tools() -> ToolsListResponse:
    registry = get_tool_registry()
    tools = registry.list_tools()
    return ToolsListResponse(tools=[ToolMetadata(**t) for t in tools])
