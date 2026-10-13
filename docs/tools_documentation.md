# 🛠️ Tool Implementation Documentation

**Project:** Nexoramind Task 05 — Intelligent Chatbot with Memory & Tool Use  
**Author:** Krishna Gupta | **Intern ID:** NM1B64D9E0  

---

## 1. Overview of Integrated Tools

The chatbot features a modular, extensible tool architecture managed by `ToolRegistry` (`core/tools/__init__.py`).  
Every tool subclasses `BaseTool` (`core/tools/base.py`) implementing two mandatory methods:
1. `can_handle(query: str) -> Tuple[bool, float]`: Pattern and keyword matching with confidence rating.
2. `run(query: str, **kwargs) -> Dict[str, Any]`: Safe deterministic execution returning formatted string responses and structured JSON payloads.

---

## 2. Integrated Tool Specifications

### 🧮 1. Calculator Tool (`core/tools/calculator.py`)
- **Purpose:** Evaluates arithmetic, percentage computations, powers, roots, and mathematical expressions safely.
- **Engine:** `sympy` (Symbolic Mathematics Library).
- **Security:** Pure AST / symbolic parsing via `sympy.sympify()`. Never uses Python's unsafe `eval()`.
- **Capabilities:**
  - Natural language percentages: *"What is 15% of 230?"* → `(15 / 100) * 230` = `34.5`
  - Multi-operator arithmetic: *"Calculate 125 * 8 + 450"* = `1450`
  - Exponents and powers: *"Evaluate 2^10"* = `1024`
  - Square roots: *"What is the square root of 144 plus 25?"* = `37`
- **Output Schema:**
  ```json
  {
    "success": true,
    "result": "Result: 34.5 (Expression: (15 / 100) * 230)",
    "tool_name": "calculator",
    "data": {
      "raw_expression": "(15 / 100) * 230",
      "result_numeric": 34.5,
      "result_display": "34.5"
    }
  }
  ```

---

### 🌤️ 2. Weather Tool (`core/tools/weather.py`)
- **Purpose:** Fetches real-time temperature, condition, humidity, and wind velocity for global cities.
- **API Integration:** OpenWeatherMap REST API (`https://api.openweathermap.org/data/2.5/weather`).
- **Resilience Strategy:** Automatically reads `OPENWEATHERMAP_API_KEY` from environment variables. If no API key is configured or when running offline, a deterministic meteorological synthesis fallback provides consistent city weather data without errors or crashes.
- **Query Patterns:**
  - *"What is the current weather in London?"*
  - *"How is the weather in Tokyo today?"*
  - *"Tell me the temperature in Delhi"*
- **Output Schema:**
  ```json
  {
    "success": true,
    "result": "Current weather in London: Mild Rain, 18°C (64.4°F). Humidity: 63%, Wind: 23.4 km/h.",
    "tool_name": "weather",
    "data": {
      "city": "London",
      "temperature_c": 18,
      "temperature_f": 64.4,
      "humidity": 63,
      "wind_speed_kmh": 23.4,
      "condition": "Mild Rain",
      "source": "OpenWeatherMap Meteorological Service"
    }
  }
  ```

---

### 📖 3. Dictionary Tool (`core/tools/dictionary.py`)
- **Purpose:** Retrieves formal definitions, lexical parts of speech, and synonyms.
- **API Integration:** Free Dictionary API (`https://api.dictionaryapi.dev/api/v2/entries/en/{word}`).
- **Resilience Strategy:** If the network request fails or when evaluating offline, falls back to a curated built-in vocabulary for common terms (*serendipity*, *resilient*, *benevolent*, *ephemeral*, etc.).
- **Query Patterns:**
  - *"Define serendipity"*
  - *"What is the meaning of resilient?"*
  - *"What are the synonyms for benevolent?"*
- **Output Schema:**
  ```json
  {
    "success": true,
    "result": "**Serendipity** (noun): The occurrence and development of events by chance in a happy or beneficial way.\n*Synonyms:* fluke, chance, happy accident, fortuity",
    "tool_name": "dictionary",
    "data": {
      "word": "serendipity",
      "part_of_speech": "noun",
      "definition": "The occurrence and development of events by chance in a happy or beneficial way.",
      "synonyms": ["fluke", "chance", "happy accident", "fortuity"]
    }
  }
  ```

---

### 🌐 4. Wikipedia Tool (`core/tools/wiki.py`)
- **Purpose:** Performs entity extraction and encyclopedic summary retrieval from Wikipedia articles.
- **API Integration:** Official `wikipedia` Python package with language set to English (`wikipedia.summary()`, `wikipedia.page()`).
- **Resilience Strategy:** Handles `DisambiguationError` by picking primary candidate topic. Also includes built-in knowledge fallback for prominent historical and computer science figures.
- **Query Patterns:**
  - *"Search wikipedia for Alan Turing"*
  - *"Who was Albert Einstein according to wikipedia?"*
- **Output Schema:**
  ```json
  {
    "success": true,
    "result": "**Alan Turing** (Wikipedia):\nAlan Turing was an English mathematician, computer scientist, logician, and cryptanalyst...",
    "tool_name": "wikipedia",
    "data": {
      "title": "Alan Turing",
      "summary": "Alan Turing was an English mathematician...",
      "url": "https://en.wikipedia.org/wiki/Alan_Turing"
    }
  }
  ```
