"""
Calculator Tool powered by SymPy.
Evaluates arithmetic expressions, percentages, powers, square roots, and algebraic terms safely.
"""

import re
from typing import Any, Dict, Tuple
import sympy
from core.tools.base import BaseTool


class CalculatorTool(BaseTool):
    """Tool for symbolic and numerical mathematical calculation."""

    name = "calculator"
    description = "Evaluates arithmetic, percentage computations, powers, roots, and mathematical expressions."

    def __init__(self):
        self.math_keywords = [
            "calculate", "compute", "solve", "what is", "evaluate",
            "+", "-", "*", "/", "^", "%", "sqrt", "power of", "percent of"
        ]

    def _extract_expression(self, query: str) -> str:
        """Extracts and normalizes math expressions from natural language."""
        q = query.lower().strip()

        # Handle percentage: "what is 15% of 230" or "15 percent of 230"
        percent_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:%|percent)\s+of\s+(\d+(?:\.\d+)?)", q)
        if percent_match:
            pct = percent_match.group(1)
            val = percent_match.group(2)
            return f"({pct} / 100) * {val}"

        # Clean introductory phrases
        for prefix in ["calculate", "compute", "solve", "what is", "evaluate", "find"]:
            if q.startswith(prefix):
                q = q[len(prefix):].strip()

        # Handle square root expressions: "square root of 144" -> "sqrt(144)"
        q = re.sub(r"\b(?:the\s+)?square root of\s+(\d+(?:\.\d+)?)", r"sqrt(\1)", q)
        q = re.sub(r"\bsqrt of\s+(\d+(?:\.\d+)?)", r"sqrt(\1)", q)

        # Remove trailing question mark or equals sign
        q = q.rstrip("?=").strip()

        # Replace textual operations
        q = re.sub(r"\btimes\b|\bmultiplied by\b", "*", q)
        q = re.sub(r"\bdivided by\b", "/", q)
        q = re.sub(r"\bplus\b", "+", q)
        q = re.sub(r"\bminus\b", "-", q)
        q = re.sub(r"\bto the power of\b", "**", q)
        q = q.replace("^", "**")

        # Keep valid math characters
        cleaned = re.sub(r"[^\d\+\-\*\/\(\)\.\,\s\w]", "", q)
        return cleaned.strip()

    def can_handle(self, query: str) -> Tuple[bool, float]:
        q = query.lower().strip()

        # Explicit percent syntax
        if re.search(r"\d+\s*(?:%|percent)\s+of\s+\d+", q):
            return True, 0.98

        # Explicit math command keywords
        if any(q.startswith(w) for w in ["calculate", "compute", "solve"]):
            return True, 0.95

        # Check for presence of operators and digits
        has_digit = bool(re.search(r"\d", q))
        has_operator = bool(re.search(r"[\+\-\*\/\^%]", q))
        is_math_query = bool(re.search(r"\b(plus|minus|times|divided|sqrt|square root)\b", q))

        if has_digit and (has_operator or is_math_query):
            if "what is" in q or "how much is" in q or has_operator:
                return True, 0.90

        return False, 0.0

    def run(self, query: str, **kwargs) -> Dict[str, Any]:
        expr_str = self._extract_expression(query)
        if not expr_str:
            return {
                "success": False,
                "result": "I could not identify a valid mathematical expression to evaluate.",
                "tool_name": self.name,
                "data": None,
            }

        try:
            # Parse and evaluate via SymPy safely (no arbitrary code execution)
            sym_expr = sympy.sympify(expr_str)
            numeric_val = sym_expr.evalf()

            # Format cleanly (remove trailing zeros for integers)
            if numeric_val == int(numeric_val):
                res_display = str(int(numeric_val))
            else:
                res_display = f"{float(numeric_val):.4f}".rstrip("0").rstrip(".")

            return {
                "success": True,
                "result": f"Result: {res_display} (Expression: {expr_str})",
                "tool_name": self.name,
                "data": {
                    "raw_expression": expr_str,
                    "result_numeric": float(numeric_val),
                    "result_display": res_display,
                },
            }
        except Exception as e:
            return {
                "success": False,
                "result": f"Could not evaluate mathematical expression '{expr_str}': {str(e)}",
                "tool_name": self.name,
                "data": {"error": str(e)},
            }
