"""
Conversational Chatbot Engine.
Coordinates multi-session memory, intent classification, tool invocation,
and context-aware response generation.
"""

from datetime import datetime
import logging
import os
import re
from typing import Any, Dict, List, Optional

from core.intent import get_intent_classifier
from core.memory import get_memory_manager
from core.tools import get_tool_registry

logger = logging.getLogger(__name__)


class ChatbotEngine:
    """Core conversational agent managing memory, tools, and response synthesis."""

    def __init__(self):
        self.memory = get_memory_manager()
        self.intent_classifier = get_intent_classifier()
        self.tool_registry = get_tool_registry()

    def _generate_chitchat_response(self, query: str) -> str:
        """Handles casual greetings and conversational small-talk."""
        q = query.lower().strip()
        if any(w in q for w in ["hi", "hello", "hey", "howdy", "greetings"]):
            return (
                "Hello! I am your AI assistant with memory and external tools (Calculator, Weather, "
                "Dictionary, Wikipedia). How can I assist you today?"
            )
        if "how are you" in q:
            return "I'm functioning smoothly and ready to assist you with calculations, weather, definitions, or research! How are you?"
        if any(w in q for w in ["who are you", "what are you"]):
            return (
                "I am an intelligent conversational chatbot built for the Nexoramind AI Engineer Program. "
                "I maintain multi-session memory, automatically classify intents, and call tools when needed."
            )
        if any(w in q for w in ["thank you", "thanks", "thx"]):
            return "You're very welcome! Let me know if you need any more calculations, definitions, or information."
        if any(w in q for w in ["bye", "goodbye", "see you"]):
            return "Goodbye! Have a productive day ahead, and feel free to return anytime."
        return "I'm here to help! Ask me anything, or try testing one of my integrated tools (Calculator, Weather, Dictionary, Wikipedia)."

    def _generate_command_response(self, query: str, session_id: str) -> str:
        """Handles session and tool management commands."""
        q = query.lower().strip()
        if any(w in q for w in ["clear", "reset", "wipe"]):
            session = self.memory.get_session(session_id)
            if session:
                session.messages.clear()
                session.summary = ""
                return f"Memory cleared for session '{session_id}'. We have a fresh conversation window."
        if any(w in q for w in ["tools", "show tools", "list tools"]):
            tools = self.tool_registry.list_tools()
            lines = [f"- **{t['name'].capitalize()}**: {t['description']}" for t in tools]
            return "Here are the tools available in my system:\n" + "\n".join(lines)
        if "help" in q:
            return (
                "**Nexoramind Chatbot Capabilities:**\n"
                "1. **Calculator**: Math expressions, roots, and percentages (e.g., *'What is 15% of 230?'*)\n"
                "2. **Weather**: City forecasts (e.g., *'Weather in Tokyo'*)\n"
                "3. **Dictionary**: Definitions & synonyms (e.g., *'Define serendipity'*)\n"
                "4. **Wikipedia**: Encyclopedic summaries (e.g., *'Search wikipedia for Alan Turing'*)\n"
                "5. **Memory**: Remembers up to 20 messages per session with automatic summarization."
            )
        return "Command acknowledged. Type 'help' to review available system operations."

    def _generate_general_question_response(self, query: str, context_history: List[Dict]) -> str:
        """Generates context-aware responses to open-ended technical questions."""
        q = query.strip()
        q_lower = q.lower()

        # Context awareness from previous turns
        prev_user_queries = [m["content"] for m in context_history if m["role"] == "user"]
        context_hint = ""
        if len(prev_user_queries) >= 2:
            last_topic = prev_user_queries[-2]
            context_hint = f"Continuing our discussion from earlier regarding '{last_topic[:30]}': "

        if "photosynthesis" in q_lower:
            return (
                f"{context_hint}Photosynthesis is the biological process used by plants, algae, and certain bacteria "
                f"to convert light energy into chemical energy stored in glucose molecules, releasing oxygen as a byproduct."
            )
        if "sky blue" in q_lower:
            return (
                f"{context_hint}The sky appears blue because of Rayleigh scattering. Earth's atmosphere scatters shorter "
                f"wavelength light (blue and violet) much more strongly than longer wavelengths (red and yellow)."
            )
        if "machine learning" in q_lower or "artificial intelligence" in q_lower:
            return (
                f"{context_hint}Machine learning is a subset of artificial intelligence focused on building algorithms "
                f"that iteratively learn patterns from empirical data rather than relying solely on explicit rule-based programming."
            )

        return (
            f"{context_hint}Regarding your question: '{q}', this involves core scientific and computational concepts. "
            f"If you need an in-depth reference, you can ask me to search Wikipedia or use one of my specialized tools."
        )

    def process_message(
        self,
        query: str,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Processes a user turn:
        1. Classifies intent (tool-use, question, command, chit-chat)
        2. Retrieves session conversation history
        3. Invokes tool if appropriate
        4. Synthesizes context-aware response
        5. Updates session memory (sliding window + auto-summary)
        """
        # Ensure session exists
        session = self.memory.get_or_create_session(session_id)
        active_session_id = session.session_id

        # 1. Classify Intent
        intent, confidence, suggested_tool_name = self.intent_classifier.classify(query)

        tool_used = None
        tool_result = None
        response_text = ""

        # 2. Execution Routing
        if intent == "tool-use" and suggested_tool_name:
            tool = self.tool_registry.get_tool(suggested_tool_name)
            if tool:
                tool_output = tool.run(query)
                tool_used = tool.name
                tool_result = tool_output
                response_text = tool_output["result"]
            else:
                response_text = "I identified a tool request, but the requested tool is unavailable."

        elif intent == "command":
            response_text = self._generate_command_response(query, active_session_id)

        elif intent == "chit-chat":
            response_text = self._generate_chitchat_response(query)

        else:  # intent == "question"
            history = self.memory.get_history(active_session_id)
            response_text = self._generate_general_question_response(query, history)

        # 3. Save into Conversation Memory
        self.memory.get_session(active_session_id).add_message(
            role="user",
            content=query,
            metadata={"intent": intent, "confidence": confidence},
        )
        self.memory.get_session(active_session_id).add_message(
            role="assistant",
            content=response_text,
            metadata={"tool_used": tool_used, "intent": intent},
        )

        return {
            "session_id": active_session_id,
            "query": query,
            "response": response_text,
            "intent": intent,
            "confidence": round(confidence, 4),
            "tool_used": tool_used,
            "tool_result": tool_result,
            "has_memory_summary": bool(session.summary),
            "session_summary": session.summary,
            "timestamp": datetime.now().isoformat(),
        }


_BOT_INSTANCE = None


def get_chatbot_engine() -> ChatbotEngine:
    """Returns singleton ChatbotEngine."""
    global _BOT_INSTANCE
    if _BOT_INSTANCE is None:
        _BOT_INSTANCE = ChatbotEngine()
    return _BOT_INSTANCE
