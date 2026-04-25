# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Highlight state container for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import State

if TYPE_CHECKING:
    from ..highlight_types import HighlightPlayer, HintStyle
    from ..primitives import Move, Square


class HighlightState(State):
    """Stores move, check, selection, and hint highlights."""

    __slots__ = "_last_move", "_check", "_selected", "_hints"

    _last_move: Move | None
    _check: Square | None
    _selected: tuple[HighlightPlayer, Square] | None
    _hints: dict[Square, tuple[HintStyle, HighlightPlayer]]

    def __init__(self) -> None:
        """Initialize the highlight state with its initial configuration."""
        self._last_move = None
        self._check = None
        self._selected = None
        self._hints = {}

    def get_last_move(self) -> Move | None:
        """Return the move currently highlighted as the last move, if any.

        Returns:
            The move currently highlighted as the last move.
        """
        return self._last_move

    def set_last_move(self, move: Move) -> None:
        """Store the move that should be highlighted as the last move.

        Args:
            move: Move to highlight as the most recently played move.
        """
        self._last_move = move

    def clear_last_move(self) -> None:
        """Clear the stored last-move highlight."""
        self._last_move = None

    def get_check(self) -> Square | None:
        """Return the square currently highlighted as check, if any.

        Returns:
            The square currently highlighted as check.
        """
        return self._check

    def set_check(self, square: Square) -> None:
        """Store the square that should be highlighted as check.

        Args:
            square: Square occupied by the king that should be shown as in check.
        """
        self._check = square

    def clear_check(self) -> None:
        """Clear the stored check highlight."""
        self._check = None

    def get_selected(self) -> tuple[HighlightPlayer, Square] | None:
        """Return the currently selected square or selection data, if any.

        Returns:
            The current selection state, or ``None`` when nothing is selected.
        """
        return self._selected

    def set_selected(self, highlight_player: HighlightPlayer, square: Square) -> None:
        """Store the selected square.

        Args:
            highlight_player: Highlight owner to use.
            square: Square that should be marked as selected.
        """
        self._selected = (highlight_player, square)

    def clear_selected(self) -> None:
        """Clear the stored selected-square highlight."""
        self._selected = None

    def get_hints(self) -> tuple[tuple[HighlightPlayer, HintStyle, Square], ...]:
        """Return the squares currently marked as move hints.

        Returns:
            tuple[tuple[HighlightPlayer, HintStyle, Square], ...]:
                Stored hint entries as ``(highlight_player, style, square)`` tuples in mapping iteration order.
        """
        return tuple((highlight_player, style, square) for square, (style, highlight_player) in self._hints.items())

    def set_hints(self, highlight_player: HighlightPlayer, hints: tuple[tuple[HintStyle, Square], ...]) -> None:
        """Set legal move hints for a square.

        Args:
            highlight_player: Highlight owner to use.
            hints: Hint squares to store.
        """
        for style, square in hints:
            self._hints[square] = (style, highlight_player)

    def add_hint(self, highlight_player: HighlightPlayer, style: HintStyle, square: Square) -> None:
        """Add a move hint for the given square.

        Args:
            highlight_player: Highlight owner to use.
            style: Highlight style to use.
            square: Destination square that should be marked as a hint.
        """
        self._hints[square] = (style, highlight_player)

    def remove_hint(self, square: Square) -> None:
        """Remove the move hint for the given square.

        Args:
            square: Hint square to remove from the stored hint mapping.
        """
        self._hints.pop(square, None)

    def clear_hints(self) -> None:
        """Clear all stored move hints."""
        self._hints = {}

    def has_highlights(self) -> bool:
        """Return whether any highlight state is currently stored.

        Returns:
            ``True`` when a last move, check square, selection, or hint is present.
        """
        return any([self._last_move is not None, self._check is not None, self._selected is not None, self._hints])

    def clear_interaction(self) -> None:
        """Clear all interaction-related highlight and selection state."""
        self.clear_selected()
        self.clear_hints()

    def clear_all(self) -> None:
        """Clear all tracked session state."""
        self.clear_interaction()
        self.clear_last_move()
        self.clear_check()
