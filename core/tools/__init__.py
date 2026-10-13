"""
Tool Registry and Dispatcher.
Maintains available tools, handles automatic intent matching, and provides execution routing.
"""

from typing import Dict, List, Optional, Tuple

from core.tools.base import BaseTool
from core.tools.calculator import CalculatorTool
from core.tools.dictionary import DictionaryTool
from core.tools.weather import WeatherTool
from core.tools.wiki import WikipediaTool


class ToolRegistry:
    """Manages active tool instances and auto-detection heuristics."""

    def __init__(self):
        self.tools: Dict[str, BaseTool] = {
            "calculator": CalculatorTool(),
            "weather": WeatherTool(),
            "dictionary": DictionaryTool(),
            "wikipedia": WikipediaTool(),
        }

    def detect_best_tool(self, query: str) -> Tuple[Optional[BaseTool], float]:
        """
        Evaluates query against all registered tools and returns best match.
        Returns:
            Tuple[Optional[BaseTool], confidence_score]
        """
        best_tool: Optional[BaseTool] = None
        best_conf = 0.0

        for tool in self.tools.values():
            can_handle, conf = tool.can_handle(query)
            if can_handle and conf > best_conf:
                best_conf = conf
                best_tool = tool

        if best_conf >= 0.5:
            return best_tool, best_conf
        return None, 0.0

    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Retrieves tool by name."""
        return self.tools.get(tool_name.lower())

    def list_tools(self) -> List[Dict[str, str]]:
        """Returns metadata for all available tools."""
        return [
            {
                "name": t.name,
                "description": t.description,
            }
            for t in self.tools.values()
        ]


_REGISTRY_INSTANCE = None


def get_tool_registry() -> ToolRegistry:
    """Returns singleton ToolRegistry."""
    global _REGISTRY_INSTANCE
    if _REGISTRY_INSTANCE is None:
        _REGISTRY_INSTANCE = ToolRegistry()
    return _REGISTRY_INSTANCE
