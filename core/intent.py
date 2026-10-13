"""
Intent Classification Engine.
Classifies user queries into: 'tool-use', 'question', 'command', or 'chit-chat'
with calculated confidence scores.
"""

import re
from typing import Optional, Tuple

from core.tools import get_tool_registry


class IntentClassifier:
    """Classifies user intent and determines tool activation."""

    def __init__(self):
        self.tool_registry = get_tool_registry()

        # Chit-chat keywords & regex
        self.chitchat_patterns = [
            r"^(hi|hello|hey|howdy|greetings|hola)\b",
            r"\b(how are you|how do you do|what's up|whats up)\b",
            r"\b(who are you|what are you|what is your name)\b",
            r"\b(thank you|thanks|thx|appreciate it)\b",
            r"^(bye|goodbye|see you|farewell)\b",
            r"^(good morning|good afternoon|good evening|good night)\b",
            r"\b(tell me a joke|are you human|are you an ai|are you real)\b",
        ]

        # Command keywords & regex
        self.command_patterns = [
            r"^(clear|reset|delete|wipe)\b",
            r"^(show|list|help|display)\s+(tools|sessions|history|commands)\b",
            r"^(switch|change|start)\s+(session|conversation)\b",
            r"^(help|menu|info)\b",
        ]

    def classify(self, query: str) -> Tuple[str, float, Optional[str]]:
        """
        Classifies user query into intent category.
        Returns:
            Tuple[intent: str, confidence: float, tool_name: Optional[str]]
        """
        q = query.strip()
        q_lower = q.lower()

        # 1. Check for Tool Use (highest priority if tool pattern matches strongly)
        matched_tool, tool_conf = self.tool_registry.detect_best_tool(q)
        if matched_tool and tool_conf >= 0.75:
            return "tool-use", tool_conf, matched_tool.name

        # 2. Check for Commands
        for cp in self.command_patterns:
            if re.search(cp, q_lower):
                return "command", 0.92, None

        # 3. Check for Chit-chat
        for ccp in self.chitchat_patterns:
            if re.search(ccp, q_lower):
                return "chit-chat", 0.94, None

        # 4. If secondary tool pattern exists with moderate confidence
        if matched_tool and tool_conf >= 0.50:
            return "tool-use", tool_conf, matched_tool.name

        # 5. Check for General Questions
        question_words = ["why", "how", "what", "where", "when", "which", "who", "can you", "explain", "describe", "tell me"]
        if any(q_lower.startswith(w) for w in question_words) or q.endswith("?"):
            return "question", 0.88, None

        # Default fallback
        if len(q.split()) <= 3:
            return "chit-chat", 0.70, None

        return "question", 0.75, None


_INTENT_INSTANCE = None


def get_intent_classifier() -> IntentClassifier:
    """Returns singleton IntentClassifier."""
    global _INTENT_INSTANCE
    if _INTENT_INSTANCE is None:
        _INTENT_INSTANCE = IntentClassifier()
    return _INTENT_INSTANCE
