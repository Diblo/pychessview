# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Normalize indentation in structured Python docstring sections."""

from __future__ import annotations

import argparse
import ast
import inspect
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final

SECTION_HEADERS: Final[frozenset[str]] = frozenset(
    {
        "Args:",
        "Arguments:",
        "Attributes:",
        "Constants:",
        "Examples:",
        "Kwargs:",
        "Parameters:",
        "Raises:",
        "Returns:",
        "Yields:",
    }
)
"""Structured docstring section headers whose bodies should be normalized."""

TRIPLE_QUOTE_PATTERN: Final[re.Pattern[str]] = re.compile(r"^([rRuUbBfF]*)(\"\"\"|''')")
"""Pattern used to read string prefixes and triple-quote delimiters from docstrings."""


@dataclass(frozen=True)
class Replacement:
    """Stores a line-based source replacement.

    Attributes:
        start_line: Zero-based first line index replaced in the source file.
        end_line: Zero-based exclusive end line index replaced in the source file.
        lines: Replacement source lines.
    """

    start_line: int
    end_line: int
    lines: tuple[str, ...]


def _docstring_expr_nodes(node: ast.AST) -> list[ast.Expr]:
    """Return docstring expression nodes contained in an AST node.

    Args:
        node: AST node to scan for leading docstring expressions.

    Returns:
        Docstring expression nodes contained in ``node`` and its nested module, class, and function bodies.
    """
    docstring_nodes: list[ast.Expr] = []

    body = getattr(node, "body", None)
    if isinstance(body, list) and body:
        first_node = body[0]  # pyright: ignore[reportUnknownVariableType]
        if (
            isinstance(first_node, ast.Expr)
            and isinstance(first_node.value, ast.Constant)
            and isinstance(first_node.value.value, str)
        ):
            docstring_nodes.append(first_node)

    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            docstring_nodes.extend(_docstring_expr_nodes(child))

    return docstring_nodes


def _normalize_section_block(lines: list[str]) -> list[str]:
    """Normalize indentation inside a docstring section body.

    Args:
        lines: Section body lines whose indentation should be normalized.

    Returns:
        Section body lines with normalized indentation.
    """
    indents = [len(line) - len(line.lstrip(" ")) for line in lines if line.strip()]
    if not indents:
        return lines

    minimum_indent = min(indents)
    normalized: list[str] = []
    for line in lines:
        stripped = line.lstrip(" ")
        if not stripped:
            normalized.append("")
            continue

        relative_indent = max(0, (len(line) - len(stripped)) - minimum_indent)
        normalized.append(f"{' ' * (4 + relative_indent)}{stripped}")

    return normalized


def _normalize_docstring_text(text: str) -> str:
    """Normalize structured section indentation in a docstring body.

    Args:
        text: Raw docstring text to normalize.

    Returns:
        Docstring text with normalized structured-section indentation.
    """
    cleaned = inspect.cleandoc(text)
    if not cleaned:
        return cleaned

    lines = cleaned.splitlines()
    normalized: list[str] = []
    line_index = 0

    while line_index < len(lines):
        line = lines[line_index].rstrip()
        normalized.append(line)
        line_index += 1

        if line.strip() not in SECTION_HEADERS:
            continue

        block: list[str] = []
        while line_index < len(lines):
            next_line = lines[line_index].rstrip()
            if next_line.strip() in SECTION_HEADERS and not next_line.startswith(" "):
                break

            block.append(next_line)
            line_index += 1

        normalized.extend(_normalize_section_block(block))

    return "\n".join(normalized)


def _build_docstring_lines(indent: str, prefix: str, quote: str, text: str) -> tuple[str, ...]:
    """Build source lines for a normalized docstring.

    Args:
        indent: Indentation that should prefix each generated source line.
        prefix: Literal string prefix used by the original docstring token.
        quote: Triple-quote delimiter used by the original docstring token.
        text: Normalized docstring body text.

    Returns:
        Source lines representing the rebuilt docstring.
    """
    if not text:
        return (f"{indent}{prefix}{quote}{quote}",)

    lines = text.splitlines()
    if len(lines) == 1:
        return (f"{indent}{prefix}{quote}{lines[0]}{quote}",)

    output = [f"{indent}{prefix}{quote}{lines[0]}"]
    output.extend(f"{indent}{line}" if line else "" for line in lines[1:])
    output.append(f"{indent}{quote}")
    return tuple(output)


def _replacement_for_docstring(source: str, expr: ast.Expr) -> Replacement | None:
    """Return a normalized replacement for a docstring expression if needed.

    Args:
        source: Full source text that contains the docstring expression.
        expr: AST expression node that stores the docstring literal.

    Returns:
        Replacement for ``expr`` when normalization changes the docstring, otherwise ``None``.
    """
    string_node = expr.value
    if not isinstance(string_node, ast.Constant) or not isinstance(string_node.value, str):
        return None
    if expr.end_lineno is None:
        return None

    segment = ast.get_source_segment(source, string_node)
    if segment is None:
        return None

    match = TRIPLE_QUOTE_PATTERN.match(segment)
    if match is None:
        return None

    prefix, quote = match.groups()
    if not segment.endswith(quote):
        return None

    raw_text = segment[len(prefix) + len(quote) : -len(quote)]
    normalized_text = _normalize_docstring_text(raw_text)

    source_lines = source.splitlines()
    indent = source_lines[expr.lineno - 1][: expr.col_offset]
    new_lines = _build_docstring_lines(indent, prefix, quote, normalized_text)

    end_lineno = expr.end_lineno
    old_lines = tuple(source_lines[expr.lineno - 1 : end_lineno])
    if old_lines == new_lines:
        return None

    return Replacement(expr.lineno - 1, end_lineno, new_lines)


def _format_docstrings(path: Path, *, check_only: bool = False) -> bool:
    """Normalize docstring section indentation in a Python source file.

    Args:
        path: Filesystem path to the Python file to inspect.
        check_only: Whether ``check_only`` should be enabled.

    Returns:
        ``True`` when the file needs or receives docstring indentation changes; otherwise, ``False``.
    """
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    replacements = [
        replacement
        for expr in _docstring_expr_nodes(tree)
        if (replacement := _replacement_for_docstring(source, expr)) is not None
    ]

    if not replacements:
        return False

    if check_only:
        return True

    lines = source.splitlines()
    for replacement in sorted(replacements, key=lambda item: item.start_line, reverse=True):
        lines[replacement.start_line : replacement.end_line] = replacement.lines

    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return True


def main(argv: list[str] | None = None) -> int:
    """Run the docstring indentation fixer.

    Args:
        argv: Optional command-line arguments for the fixer.

    Returns:
        Process exit status for the fixer command.
    """
    parser = argparse.ArgumentParser(description="Normalize indentation in structured Python docstrings.")
    parser.add_argument("--check", action="store_true", help="Check files without writing changes.")
    parser.add_argument("paths", nargs="+", help="Python files to inspect.")
    args = parser.parse_args(argv)

    changed_paths: list[Path] = []
    has_pending_changes = False
    for raw_path in args.paths:
        path = Path(raw_path)
        if not path.is_file() or path.suffix != ".py":
            continue

        if not _format_docstrings(path, check_only=args.check):
            continue

        has_pending_changes = True
        if not args.check:
            changed_paths.append(path)

    if not has_pending_changes:
        return 0

    for path in changed_paths:
        print(f"normalized docstrings in {path}")

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
