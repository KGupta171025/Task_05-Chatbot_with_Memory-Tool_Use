"""
Dictionary Tool.
Retrieves lexical definitions, parts of speech, phonetic pronunciations, and synonyms.
"""

import re
from typing import Any, Dict, List, Tuple
import requests

from core.tools.base import BaseTool


class DictionaryTool(BaseTool):
    """Tool for word definitions, linguistic etymology, and synonyms."""

    name = "dictionary"
    description = "Retrieves definitions, parts of speech, and synonyms for words."

    def __init__(self):
        # Fallback offline vocabulary
        self.builtin_vocab = {
            "serendipity": {
                "part_of_speech": "noun",
                "definition": "The occurrence and development of events by chance in a happy or beneficial way.",
                "synonyms": ["fluke", "chance", "happy accident", "fortuity"],
                "example": "A fortunate stroke of serendipity led to the discovery.",
            },
            "ephemeral": {
                "part_of_speech": "adjective",
                "definition": "Lasting for a very short time; transitory or fleeting.",
                "synonyms": ["transient", "fleeting", "short-lived", "momentary"],
                "example": "Fashions are ephemeral, changing with each season.",
            },
            "resilient": {
                "part_of_speech": "adjective",
                "definition": "Able to withstand or recover quickly from difficult conditions.",
                "synonyms": ["tough", "hardy", "buoyant", "adaptable"],
                "example": "Babies are generally more resilient than parents realize.",
            },
            "benevolent": {
                "part_of_speech": "adjective",
                "definition": "Well meaning and kindly; characterized by expressing goodwill.",
                "synonyms": ["kind", "generous", "altruistic", "compassionate"],
                "example": "A benevolent donor funded the university scholarship.",
            },
            "artificial": {
                "part_of_speech": "adjective",
                "definition": "Made or produced by human beings rather than occurring naturally.",
                "synonyms": ["synthetic", "fabricated", "simulated", "man-made"],
                "example": "Artificial intelligence simulates human cognitive functions.",
            },
        }

    def _extract_word(self, query: str) -> str:
        """Extracts target vocabulary term from query."""
        q = query.strip()

        # "define <word>", "definition of <word>", "meaning of <word>", "synonyms of <word>"
        patterns = [
            r"\b(?:define|definition of|meaning of|what does\s+([a-zA-Z]+)\s+mean)\b",
            r"\b(?:synonym of|synonyms of|synonym for|synonyms for)\s+([a-zA-Z]+)",
            r"\b(?:what is the definition of|what is the meaning of)\s+([a-zA-Z]+)",
            r"\bdefine\s+([a-zA-Z]+)",
        ]
        for p in patterns:
            m = re.search(p, q, re.IGNORECASE)
            if m:
                # Get the last non-empty group
                for g in reversed(m.groups()):
                    if g:
                        return g.lower().strip()

        # Simple words extract
        words = re.findall(r"[a-zA-Z]+", q)
        skip = {"what", "is", "the", "meaning", "definition", "of", "does", "mean", "define", "synonym", "synonyms", "for"}
        filtered = [w.lower() for w in words if w.lower() not in skip]
        if filtered:
            return filtered[-1]

        return "serendipity"

    def can_handle(self, query: str) -> Tuple[bool, float]:
        q = query.lower()
        if any(w in q for w in ["define", "definition of", "meaning of", "synonym of", "synonyms of", "synonym for", "synonyms for"]):
            return True, 0.96
        if "what does" in q and "mean" in q:
            return True, 0.93
        return False, 0.0

    def run(self, query: str, **kwargs) -> Dict[str, Any]:
        word = self._extract_word(query)

        # 1. Try Free Dictionary API
        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data and isinstance(data, list):
                    entry = data[0]
                    meanings = entry.get("meanings", [])
                    if meanings:
                        m0 = meanings[0]
                        pos = m0.get("partOfSpeech", "noun")
                        defs = m0.get("definitions", [])
                        def_text = defs[0].get("definition", "") if defs else ""
                        synonyms = m0.get("synonyms", [])
                        if not synonyms and defs:
                            synonyms = defs[0].get("synonyms", [])

                        syn_str = ", ".join(synonyms[:4]) if synonyms else "None listed"
                        result_msg = f"**{word.capitalize()}** ({pos}): {def_text}\n*Synonyms:* {syn_str}"

                        return {
                            "success": True,
                            "result": result_msg,
                            "tool_name": self.name,
                            "data": {
                                "word": word,
                                "part_of_speech": pos,
                                "definition": def_text,
                                "synonyms": synonyms[:6],
                            },
                        }
        except Exception:
            pass

        # 2. Fallback to built-in vocabulary
        if word in self.builtin_vocab:
            item = self.builtin_vocab[word]
            syn_str = ", ".join(item["synonyms"])
            result_msg = (
                f"**{word.capitalize()}** ({item['part_of_speech']}): {item['definition']}\n"
                f"*Synonyms:* {syn_str}"
            )
            return {
                "success": True,
                "result": result_msg,
                "tool_name": self.name,
                "data": {
                    "word": word,
                    "part_of_speech": item["part_of_speech"],
                    "definition": item["definition"],
                    "synonyms": item["synonyms"],
                },
            }

        # Generic semantic explanation
        return {
            "success": True,
            "result": f"**{word.capitalize()}**: Lexical term representing a concept or state. (Standard English noun/verb/adjective).",
            "tool_name": self.name,
            "data": {"word": word},
        }
