"""
System Configuration and Constants for Task 05 Chatbot.
"""

from pathlib import Path
from typing import List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
EVALUATION_DIR = PROJECT_ROOT / "evaluation"
ASSETS_DIR = PROJECT_ROOT / "assets"
SCREENSHOTS_DIR = ASSETS_DIR / "screenshots"

DOCS_DIR.mkdir(parents=True, exist_ok=True)
EVALUATION_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# Memory settings (per assignment requirements: last 20 messages per session)
MAX_HISTORY_MESSAGES: int = 20
AUTO_SUMMARIZE_THRESHOLD: int = 20

# Intent categories
INTENT_CATEGORIES: List[str] = ["tool-use", "question", "command", "chit-chat"]

# API specifications
API_TITLE = "Nexoramind Chatbot with Memory & Tool Use API"
API_VERSION = "1.0.0"
API_DESCRIPTION = (
    "Production conversational chatbot engine supporting multi-session sliding window memory, "
    "automatic summarization, rule/semantic intent classification, and multi-tool orchestration "
    "(Calculator, Weather, Dictionary, Wikipedia)."
)
