# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Promotion state container for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..exceptions import StateError
from ..primitives import File, Move, PlayerColor, Rank, Square
from .base import State

if TYPE_CHECKING:
    from ..primitives import Piece


class PromotionState(State):
    """Stores the active promotion chooser state."""

    __slots__ = "_white_promotion_pieces", "_black_promotion_pieces", "_move", "_color", "_highlighted", "_show"

    _white_promotion_pieces: tuple[Piece, ...]
    _black_promotion_pieces: tuple[Piece, ...]

    _move: Move
    _color: PlayerColor
    _highlighted: int | None

    _show: bool

    def __init__(self, white_promotion_pieces: tuple[Piece, ...], black_promotion_pieces: tuple[Piece, ...]) -> None:
        """Initialize the promotion state with its initial configuration.

        Args:
            white_promotion_pieces: Value used to initialize ``white_promotion_pieces``.
            black_promotion_pieces: Value used to initialize ``black_promotion_pieces``.
        """
        if not 0 <= len(white_promotion_pieces) <= 8 or not 0 <= len(black_promotion_pieces) <= 8:
            raise StateError("promotion pieces must contain between 0 and 8 entries")

        self._white_promotion_pieces = white_promotion_pieces
        self._black_promotion_pieces = black_promotion_pieces
        self._move = Move(Square(File.A, Rank.ONE), Square(File.A, Rank.ONE))
        self._color = PlayerColor.WHITE
        self._highlighted = None

        self._show = False

    @property
    def white_promotion_pieces(self) -> tuple[Piece, ...]:
        """Promotion pieces available to white.

        Returns:
            Promotion pieces available to white.
        """
        return self._white_promotion_pieces

    @white_promotion_pieces.setter
    def white_promotion_pieces(self, pieces: tuple[Piece, ...]) -> None:
        """Promotion piece options available for white.

        Args:
            pieces: Sequence of pieces the white player may choose from during promotion.
        """
        if not 0 <= len(pieces) <= 8:
            raise StateError("promotion pieces must contain between 0 and 8 entries")
        self._white_promotion_pieces = pieces

    @property
    def black_promotion_pieces(self) -> tuple[Piece, ...]:
        """Promotion pieces available to black.

        Returns:
            Promotion pieces available to black.
        """
        return self._black_promotion_pieces

    @black_promotion_pieces.setter
    def black_promotion_pieces(self, pieces: tuple[Piece, ...]) -> None:
        """Promotion piece options available for black.

        Args:
            pieces: Sequence of pieces the black player may choose from during promotion.
        """
        if not 0 <= len(pieces) <= 8:
            raise StateError("promotion pieces must contain between 0 and 8 entries")
        self._black_promotion_pieces = pieces

    @property
    def move(self) -> Move:
        """Promotion move currently being resolved.

        Returns:
            Promotion move currently being resolved.
        """
        return self._move

    @property
    def color(self) -> PlayerColor:
        """Active promotion color.

        Returns:
            Active promotion color.
        """
        return self._color

    def show_promotion(self, move: Move, player: PlayerColor) -> None:
        """Activate the promotion chooser for a pending promotion move.

        Args:
            move: Promotion move whose destination file and rank determine the chooser layout.
            player: Color whose promotion piece options should be exposed.
        """
        if move.to_square.rank not in (Rank.ONE, Rank.EIGHT):
            raise StateError(f"invalid promotion move target: {move.to_square}, rank must be 1 or 8")
        self._move = move
        self._color = player
        self._show = True

    def is_active(self) -> bool:
        """Return whether the promotion chooser is currently visible.

        Returns:
            ``True`` when a promotion move is waiting for a piece selection.
        """
        return self._show

    def clear_promotion(self) -> None:
        """Clear all promotion state."""
        self._show = False
        self.clear_highlight()

    @property
    def highlighted(self) -> int | None:
        """Highlighted promotion index, if any.

        Returns:
            Highlighted promotion index, if any.
        """
        return self._highlighted

    def set_highlight(self, index: int) -> None:
        """Store the highlighted promotion index.

        Args:
            index: Zero-based index of the promotion option currently under the pointer.
        """
        self._highlighted = index

    def clear_highlight(self) -> None:
        """Clear the highlighted promotion index."""
        self._highlighted = None

    def is_valid_index(self, index: int) -> bool:
        """Return whether ``index`` refers to an available promotion option for the active color.

        Args:
            index: Zero-based promotion option index to validate.

        Returns:
            ``True`` when ``index`` is within the configured promotion piece list for the active color.
        """
        if self._color is PlayerColor.WHITE:
            return 0 <= index < len(self._white_promotion_pieces)
        return 0 <= index < len(self._black_promotion_pieces)

    def get_piece(self, index: int) -> Piece:
        """Return the promotion piece associated with the given promotion index.

        Args:
            index: Zero-based promotion option index for the active color.

        Returns:
            The promotion piece stored at ``index`` for the active color.
        """
        if self._color is PlayerColor.WHITE:
            return self._white_promotion_pieces[index]
        return self._black_promotion_pieces[index]

    def clear_all(self) -> None:
        """Clear all tracked session state."""
        self.clear_promotion()
        self.clear_highlight()
