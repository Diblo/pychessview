# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Piece UI state container for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import State

if TYPE_CHECKING:
    from ...layout.primitives import Coord
    from ..domain.adapters.protocol import GameAdapterProtocol
    from ..primitives import Move, Piece, Square


class PieceUiState(State):
    """Stores drag-and-drop piece UI state."""

    __slots__ = "_game_adapter", "_dragged_square", "_dragged_position", "_preview_move"

    _game_adapter: GameAdapterProtocol
    _dragged_square: Square | None
    _dragged_position: Coord | None
    _preview_move: Move | None

    def __init__(self, game_adapter: GameAdapterProtocol) -> None:
        """Initialize the piece ui state with its initial configuration.

        Args:
            game_adapter: Game adapter used to provide board state and rule queries.
        """
        self._game_adapter = game_adapter
        self._dragged_square = None
        self._dragged_position = None
        self._preview_move = None

    def pieces(self) -> dict[Square, Piece]:
        """Return the current piece placement as a mapping from occupied squares to pieces.

        Returns:
            Mapping of occupied squares to their pieces.
        """
        return self._game_adapter.pieces()

    @property
    def preview_move(self) -> Move | None:
        """Move currently shown as a preview in the UI.

        Returns:
            Move currently shown as a preview in the UI.
        """
        return self._preview_move

    @preview_move.setter
    def preview_move(self, move: Move | None) -> None:
        """Store the piece and coordinate used for drag preview rendering.

        Args:
            move: Move to display as the current preview, or ``None`` to clear it.
        """
        self._preview_move = move

    @property
    def dragged_square(self) -> Square | None:
        """Square of the piece currently being dragged.

        Returns:
            Square of the piece currently being dragged.
        """
        return self._dragged_square

    @property
    def dragged_position(self) -> Coord | None:
        """Current pointer position for the dragged piece.

        Returns:
            Current pointer position for the dragged piece.
        """
        return self._dragged_position

    def set_dragged_piece(self, square: Square, position: Coord) -> None:
        """Store the piece currently being dragged.

        Args:
            square: Square the dragged piece originated from.
            position: Current pointer position for the dragged piece.
        """
        self._dragged_square = square
        self._dragged_position = position

    def set_dragged_position(self, position: Coord) -> None:
        """Store the current drag position in viewport coordinates.

        Args:
            position: Updated pointer position for the dragged piece.
        """
        self._dragged_position = position

    def is_dragging(self) -> bool:
        """Return whether a drag operation is currently in progress.

        Returns:
            ``True`` when both the dragged source square and pointer position are set.
        """
        return self._dragged_square is not None and self._dragged_position is not None

    def clear_dragged_piece(self) -> None:
        """Clear the stored dragged piece."""
        self._dragged_square = None
        self._dragged_position = None

    def clear_all(self) -> None:
        """Clear all tracked session state."""
        self._preview_move = None
        self.clear_dragged_piece()
