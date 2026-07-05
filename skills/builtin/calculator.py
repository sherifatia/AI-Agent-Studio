"""Skill: calculator — evaluates a safe arithmetic expression."""

from __future__ import annotations

import ast
import operator
from typing import Any

from skills.skill import BaseSkill, SkillResult

# Allowed operators — no function calls, no attribute access.
_OPERATORS: dict[type, Any] = {
    ast.Add:  operator.add,
    ast.Sub:  operator.sub,
    ast.Mult: operator.mul,
    ast.Div:  operator.truediv,
    ast.Pow:  operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
    ast.Mod:  operator.mod,
}

_MAX_INPUT_LEN = 200


def _safe_eval(node: ast.expr) -> float:
    """Recursively evaluate an AST node using only allowed operators.

    Raises:
        ValueError: For any unsupported node type or division by zero.
    """
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError(f"Unsupported constant type: {type(node.value)}")

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _OPERATORS:
            raise ValueError(f"Unsupported operator: {op_type.__name__}")
        left  = _safe_eval(node.left)
        right = _safe_eval(node.right)
        if op_type is ast.Div and right == 0:
            raise ValueError("Division by zero")
        return _OPERATORS[op_type](left, right)

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _OPERATORS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        return _OPERATORS[op_type](_safe_eval(node.operand))

    raise ValueError(f"Unsupported expression node: {type(node).__name__}")


class CalculatorSkill(BaseSkill):
    """Evaluates a simple arithmetic expression using a safe AST evaluator.

    Supports: ``+ - * / ** %`` and parentheses.
    Does NOT support: function calls, variable names, imports, or any
    Python construct beyond plain numeric arithmetic.
    """

    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Evaluate a safe arithmetic expression (e.g. '2 + 3 * 4')."

    def execute(self, input: str) -> SkillResult:
        """Evaluate ``input`` as an arithmetic expression.

        Args:
            input: A string containing an arithmetic expression,
                   e.g. ``"(3 + 4) * 2"`` or ``"10 / 3"``.

        Returns:
            A ``SkillResult`` with the numeric answer as the output string,
            or a failed result with an error description.
        """
        expr = input.strip()
        if not expr:
            return SkillResult(
                success=False, output="", error="No expression provided."
            )
        if len(expr) > _MAX_INPUT_LEN:
            return SkillResult(
                success=False,
                output="",
                error=f"Expression too long (max {_MAX_INPUT_LEN} chars).",
            )

        try:
            tree = ast.parse(expr, mode="eval")
            value = _safe_eval(tree.body)
            # Format as integer when the result is whole
            formatted = str(int(value)) if value == int(value) else str(value)
            return SkillResult(
                success=True,
                output=f"{expr} = {formatted}",
                metadata={"expression": expr, "result": value},
            )
        except (SyntaxError, ValueError) as exc:
            return SkillResult(success=False, output="", error=str(exc))
