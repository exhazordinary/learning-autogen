"""Calculator tool for agents."""

import ast
import json
import math
import operator
from typing import Annotated, Any

from ..utils.logger import get_logger

logger = get_logger(__name__)


# Safe operators for math evaluation
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# Safe functions
SAFE_FUNCTIONS = {
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "pi": math.pi,
    "e": math.e,
}


def _safe_eval(node):
    """Safely evaluate a math expression AST node."""
    if isinstance(node, ast.Num):  # number
        return node.n
    elif isinstance(node, ast.BinOp):  # binary operation
        op = SAFE_OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
        return op(_safe_eval(node.left), _safe_eval(node.right))
    elif isinstance(node, ast.UnaryOp):  # unary operation
        op = SAFE_OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
        return op(_safe_eval(node.operand))
    elif isinstance(node, ast.Call):  # function call
        func_name = node.func.id if isinstance(node.func, ast.Name) else None
        if func_name not in SAFE_FUNCTIONS:
            raise ValueError(f"Unsupported function: {func_name}")
        func = SAFE_FUNCTIONS[func_name]
        args = [_safe_eval(arg) for arg in node.args]
        return func(*args)
    elif isinstance(node, ast.Name):  # constant like pi, e
        if node.id in SAFE_FUNCTIONS:
            return SAFE_FUNCTIONS[node.id]
        raise ValueError(f"Unsupported name: {node.id}")
    else:
        raise ValueError(f"Unsupported expression: {type(node).__name__}")


def calculator(expression: Annotated[str, "Mathematical expression to evaluate"]) -> str:
    """
    Safely evaluate a mathematical expression.

    Supports basic arithmetic, common math functions, and constants.

    Supported operations: +, -, *, /, //, %, **
    Supported functions: abs, round, min, max, sum, sqrt, sin, cos, tan, log, log10, exp
    Supported constants: pi, e

    Args:
        expression: Mathematical expression as string

    Returns:
        JSON string with result or error
    """
    logger.info(f"Evaluating: {expression}")

    try:
        # Parse expression into AST
        tree = ast.parse(expression, mode="eval")

        # Evaluate safely
        result = _safe_eval(tree.body)

        return json.dumps({"status": "success", "expression": expression, "result": result})

    except ZeroDivisionError:
        return json.dumps({"status": "error", "message": "Division by zero"})
    except Exception as e:
        logger.error(f"Calculator error: {e}")
        return json.dumps({"status": "error", "message": f"Evaluation failed: {str(e)}"})


class CalculatorTool:
    """Calculator tool wrapper for AutoGen."""

    @staticmethod
    def get_schema() -> dict[str, Any]:
        """Get tool schema for AutoGen."""
        return {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": (
                    "Evaluate mathematical expressions. "
                    "Supports arithmetic, common functions (sqrt, sin, cos, log, etc.), "
                    "and constants (pi, e)"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate (e.g., '2 + 2', 'sqrt(16)', 'sin(pi/2)')",
                        }
                    },
                    "required": ["expression"],
                },
            },
        }

    @staticmethod
    def execute(expression: str) -> str:
        """Execute calculator."""
        return calculator(expression)
