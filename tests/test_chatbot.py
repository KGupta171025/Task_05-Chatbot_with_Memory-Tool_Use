"""
Unit and Integration Tests for Task 05 Chatbot with Memory and Tool Use.
"""

import pytest
from fastapi.testclient import TestClient

from api.app import app
from core.bot import get_chatbot_engine
from core.intent import get_intent_classifier
from core.memory import get_memory_manager
from core.tools import get_tool_registry
from core.tools.calculator import CalculatorTool
from core.tools.dictionary import DictionaryTool
from core.tools.weather import WeatherTool
from core.tools.wiki import WikipediaTool

client = TestClient(app)


# ==================== MEMORY TESTS ====================

class TestMemoryManager:
    def test_session_lifecycle(self):
        mem = get_memory_manager()
        s = mem.create_session("test_sess_01", title="Test Session")
        assert s.session_id == "test_sess_01"
        assert s.title == "Test Session"

        retrieved = mem.get_session("test_sess_01")
        assert retrieved is not None
        assert retrieved.session_id == "test_sess_01"

        deleted = mem.delete_session("test_sess_01")
        assert deleted is True
        assert mem.get_session("test_sess_01") is None

    def test_sliding_window_memory_limit_20(self):
        """Verifies sliding window limits memory to last 20 messages."""
        mem = get_memory_manager()
        s = mem.create_session("limit_test_sess")

        # Add 30 messages
        for i in range(30):
            s.add_message(role="user" if i % 2 == 0 else "assistant", content=f"Message {i}")

        # Active messages must be capped at 20
        assert len(s.messages) == 20
        assert s.total_messages_count == 30
        assert "Message 29" in s.messages[-1].content

    def test_auto_summarization(self):
        """Verifies older messages are compressed into session summary."""
        mem = get_memory_manager()
        s = mem.create_session("summary_test_sess")

        for i in range(25):
            s.add_message(role="user", content=f"Topic discussion turn {i}")

        assert bool(s.summary) is True
        assert "Earlier conversation topics" in s.summary


# ==================== TOOL TESTS ====================

class TestTools:
    def test_calculator_percentage(self):
        calc = CalculatorTool()
        can, conf = calc.can_handle("What is 15% of 230?")
        assert can is True
        assert conf > 0.8
        res = calc.run("What is 15% of 230?")
        assert res["success"] is True
        assert "34.5" in res["result"]

    def test_calculator_arithmetic_and_roots(self):
        calc = CalculatorTool()
        res1 = calc.run("Calculate 125 * 8 + 450")
        assert res1["success"] is True
        assert "1450" in res1["result"]

        res2 = calc.run("What is the square root of 144 plus 25?")
        assert res2["success"] is True
        assert "37" in res2["result"]

    def test_weather_tool(self):
        weather = WeatherTool()
        can, conf = weather.can_handle("What is the current weather in London?")
        assert can is True
        assert conf > 0.8
        res = weather.run("What is the current weather in London?")
        assert res["success"] is True
        assert "London" in res["result"]
        assert "temperature_c" in res["data"]

    def test_dictionary_tool(self):
        dt = DictionaryTool()
        can, conf = dt.can_handle("Define serendipity")
        assert can is True
        assert conf > 0.8
        res = dt.run("Define serendipity")
        assert res["success"] is True
        assert "Serendipity" in res["result"]

    def test_wikipedia_tool(self):
        wiki = WikipediaTool()
        can, conf = wiki.can_handle("Search wikipedia for Alan Turing")
        assert can is True
        assert conf > 0.8
        res = wiki.run("Search wikipedia for Alan Turing")
        assert res["success"] is True
        assert "Alan Turing" in res["result"]


# ==================== INTENT TESTS ====================

class TestIntentClassifier:
    def test_classify_tool_use(self):
        clf = get_intent_classifier()
        intent, conf, tool = clf.classify("What is 15% of 230?")
        assert intent == "tool-use"
        assert tool == "calculator"
        assert conf > 0.8

    def test_classify_chitchat(self):
        clf = get_intent_classifier()
        intent, conf, _ = clf.classify("Hello there, how are you?")
        assert intent == "chit-chat"
        assert conf > 0.8

    def test_classify_command(self):
        clf = get_intent_classifier()
        intent, conf, _ = clf.classify("Show tools available in system")
        assert intent == "command"
        assert conf > 0.8

    def test_classify_general_question(self):
        clf = get_intent_classifier()
        intent, conf, _ = clf.classify("Why is the sky blue?")
        assert intent == "question"
        assert conf > 0.7


# ==================== API TESTS ====================

class TestAPI:
    def test_root_endpoint(self):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "endpoints" in resp.json()

    def test_health_endpoint(self):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "calculator" in data["available_tools"]

    def test_tools_list_endpoint(self):
        resp = client.get("/api/tools")
        assert resp.status_code == 200
        tools = resp.json()["tools"]
        assert len(tools) == 4

    def test_session_management_endpoints(self):
        # Create
        create_resp = client.post("/api/session/new", json={"title": "Integration Test Session"})
        assert create_resp.status_code == 200
        sid = create_resp.json()["session_id"]

        # List
        list_resp = client.get("/api/session")
        assert list_resp.status_code == 200
        sids = [s["session_id"] for s in list_resp.json()["sessions"]]
        assert sid in sids

        # History
        hist_resp = client.get(f"/api/session/{sid}/history")
        assert hist_resp.status_code == 200
        assert hist_resp.json()["total_active_messages"] == 0

        # Delete
        del_resp = client.delete(f"/api/session/{sid}")
        assert del_resp.status_code == 200
        assert del_resp.json()["success"] is True

    def test_chat_endpoint_with_tool_call(self):
        payload = {"message": "What is 15% of 230?"}
        resp = client.post("/api/chat", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["intent"] == "tool-use"
        assert data["tool_used"] == "calculator"
        assert "34.5" in data["response"]
