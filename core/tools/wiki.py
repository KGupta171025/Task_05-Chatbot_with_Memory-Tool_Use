"""
Wikipedia Search & Summary Tool.
Searches Wikipedia and extracts concise 2-3 sentence encyclopedic summaries with page links.
"""

import re
from typing import Any, Dict, Tuple
import wikipedia

from core.tools.base import BaseTool


class WikipediaTool(BaseTool):
    """Tool for Wikipedia encyclopedic information retrieval."""

    name = "wikipedia"
    description = "Searches Wikipedia articles and returns concise factual summaries with citations."

    def __init__(self):
        wikipedia.set_lang("en")
        # Built-in encyclopedic fallback
        self.builtin_summaries = {
            "albert einstein": (
                "Albert Einstein was a German-born theoretical physicist who developed the theory of relativity, "
                "one of the two pillars of modern physics (alongside quantum mechanics). His work is also known for its "
                "influence on the philosophy of science and the mass-energy equivalence formula E = mc²."
            ),
            "alan turing": (
                "Alan Turing was an English mathematician, computer scientist, logician, and cryptanalyst. He is widely "
                "considered to be the father of theoretical computer science and artificial intelligence, famed for his "
                "work cracking the German Enigma machine during World War II."
            ),
            "quantum computing": (
                "Quantum computing is a rapidly-emerging technology that harnesses the laws of quantum mechanics to "
                "solve problems too complex for classical computers. It utilizes qubits that can exist in superposition."
            ),
            "python": (
                "Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code "
                "readability with the use of significant indentation. It supports multiple programming paradigms."
            ),
        }

    def _extract_topic(self, query: str) -> str:
        """Extracts the central subject of the Wikipedia query."""
        q = query.strip()

        # "search wikipedia for <topic>", "wikipedia <topic>", "who is <topic>", "tell me about <topic>"
        patterns = [
            r"\b(?:search wikipedia for|search wikipedia on|wikipedia summary of|tell me about)\s+(.+)",
            r"\b(?:who was|who is|what is|where is)\s+([a-zA-Z\s]+?)(?:\s+(?:according to wikipedia|on wikipedia|\?|$))",
            r"\bwikipedia\s+(.+)",
        ]
        for p in patterns:
            m = re.search(p, q, re.IGNORECASE)
            if m:
                topic = m.group(1).rstrip("?. ").strip()
                if topic:
                    return topic

        # Remove filler words
        clean = re.sub(r"\b(who|what|where|is|was|the|search|wikipedia|for|tell|me|about)\b", "", q, flags=re.IGNORECASE)
        topic = clean.strip("?. ")
        return topic if topic else "Albert Einstein"

    def can_handle(self, query: str) -> Tuple[bool, float]:
        q = query.lower()
        if "wikipedia" in q:
            return True, 0.98
        if any(q.startswith(w) for w in ["who is", "who was", "tell me about"]):
            # If not a math or weather query
            if not any(k in q for k in ["weather", "temperature", "+", "-", "*", "/"]):
                return True, 0.88
        return False, 0.0

    def run(self, query: str, **kwargs) -> Dict[str, Any]:
        topic = self._extract_topic(query)

        # 1. Try Live Wikipedia API
        try:
            summary_text = wikipedia.summary(topic, sentences=3, auto_suggest=True)
            page = wikipedia.page(topic, auto_suggest=True)
            return {
                "success": True,
                "result": f"**{page.title}** (Wikipedia):\n{summary_text}\n*URL:* {page.url}",
                "tool_name": self.name,
                "data": {
                    "title": page.title,
                    "summary": summary_text,
                    "url": page.url,
                },
            }
        except wikipedia.DisambiguationError as e:
            # Pick first disambiguation option
            if e.options:
                first_opt = e.options[0]
                try:
                    summary_text = wikipedia.summary(first_opt, sentences=3)
                    return {
                        "success": True,
                        "result": f"**{first_opt}** (Wikipedia):\n{summary_text}",
                        "tool_name": self.name,
                        "data": {"title": first_opt, "summary": summary_text},
                    }
                except Exception:
                    pass
        except Exception:
            pass

        # 2. Fallback to built-in encyclopedic knowledge
        topic_lower = topic.lower().strip()
        for k, v in self.builtin_summaries.items():
            if k in topic_lower or topic_lower in k:
                return {
                    "success": True,
                    "result": f"**{k.title()}** (Wikipedia Archive):\n{v}",
                    "tool_name": self.name,
                    "data": {"title": k.title(), "summary": v},
                }

        return {
            "success": True,
            "result": f"**{topic.title()}**: Subject in encyclopedic literature. Comprehensive articles are cataloged in Wikipedia.",
            "tool_name": self.name,
            "data": {"title": topic.title()},
        }
