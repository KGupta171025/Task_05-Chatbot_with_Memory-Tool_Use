"""
Base Tool Interface for Chatbot Tool Calling.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple


class BaseTool(ABC):
    """Abstract base class for all callable tools."""

    name: str = "base_tool"
    description: str = "Base tool description."

    @abstractmethod
    def can_handle(self, query: str) -> Tuple[bool, float]:
        """
        Determines whether this tool should handle the query and with what confidence.
        Returns:
            Tuple[bool, float]: (can_handle, confidence_score between 0.0 and 1.0)
        """
        pass

    @abstractmethod
    def run(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Executes the tool on the given user query.
        Returns:
            Dict containing:
                success: bool
                result: str (human-readable response)
                tool_name: str
                data: Any (structured payload)
        """
        pass
