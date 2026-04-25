# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Define the protocol for game adapters that provide board state and chess rules."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ...primitives import Move, Piece, PlayerColor, Square


class GameAdapterProtocol(Protocol):
    """Define the protocol for game adapters that expose board state and enforce chess rules."""

    @property
    def default_fen(self) -> str:
        """Return the FEN string used when the adapter is reset to its default position."""
        ...

    @default_fen.setter
    def default_fen(self, fen: str) -> None:
        """Set the default FEN used for future resets.

        Args:
            fen: FEN string to store as the reset position.
        """
        ...

    @property
    def fen(self) -> str:
        """Return the adapter's current position as a FEN string.

        Implementations may derive this value from live board state or may return a stored FEN string,
        depending on how they represent the underlying position.
        """
        ...

    @fen.setter
    def fen(self, fen: str) -> None:
        """Update the adapter's current position from a FEN string.

        Implementations may support either full FEN strings or only piece-placement FEN strings.
        Any limitations should be documented by the concrete adapter.

        Args:
            fen: FEN string describing the position to store or load.
        """
        ...

    @property
    def turn(self) -> PlayerColor:
        """Return the color of the player whose turn it is to move."""
        ...

    def pieces(self) -> dict[Square, Piece]:
        """Return the current piece placement as a mapping of occupied squares to pieces.

        Returns:
            Mapping containing only occupied squares. Concrete adapters may return either a snapshot
            copy or a newly constructed mapping, but callers should treat the result as read-only.
        """
        ...

    def piece_at(self, square: Square) -> Piece | None:
        """Return the piece currently placed on a square, if any.

        Args:
            square: Board square to inspect.

        Returns:
            The piece on ``square``, or ``None`` if the square is empty.
        """
        ...

    def set_piece(self, square: Square, piece: Piece | None) -> None:
        """Set or clear the piece on a square.

        Args:
            square: Board square to modify.
            piece: Piece to place on ``square``, or ``None`` to clear it.
        """
        ...

    def king(self, color: PlayerColor) -> Square | None:
        """Return the square occupied by the specified king, if present.

        Args:
            color: Color of the king to locate.

        Returns:
            Square occupied by the king of ``color``, or ``None`` if no such king is present.
        """
        ...

    def is_legal_move(self, move: Move) -> bool:
        """Return whether a move is legal in the current position.

        Args:
            move: Move to validate.

        Returns:
            ``True`` if ``move`` is legal in the current position; otherwise, ``False``.
        """
        ...

    def is_promotion_move(self, move: Move) -> bool:
        """Return whether a move requires a promotion choice.

        Args:
            move: Move to evaluate.

        Returns:
            ``True`` if ``move`` requires promotion; otherwise, ``False``.
        """
        ...

    def has_move_history(self) -> bool:
        """Return whether at least one move has been recorded.

        Returns:
            ``True`` if at least one move has been recorded; otherwise, ``False``.
        """
        ...

    @property
    def move_history(self) -> tuple[Move, ...]:
        """Return the moves recorded for the current game state in play order."""
        ...

    def move(self, move: Move) -> None:
        """Apply a move to the current game state.

        Implementations may assume that legality has already been checked, or they may reject illegal
        moves according to backend-specific rules.

        Args:
            move: Move to apply.
        """
        ...

    def is_check(self) -> bool:
        """Return whether the side to move is currently in check.

        Returns:
            ``True`` if the side to move is in check; otherwise, ``False``.
        """
        ...

    def is_checkmate(self) -> bool:
        """Return whether the current position is checkmate.

        Returns:
            ``True`` if the side to move is checkmated; otherwise, ``False``.
        """
        ...

    def get_legal_hints(self, square: Square) -> set[Square]:
        """Return legal destination squares for the piece on a square.

        Args:
            square: Board square containing the piece to evaluate.

        Returns:
            Destination squares that can be reached by legal moves from ``square``. Returns an empty
            set when no legal moves are available or when ``square`` does not contain a movable piece.
        """
        ...

    def get_pseudo_legal_hints(self, square: Square, color: PlayerColor) -> set[Square]:
        """Return pseudo-legal destination squares for the piece on a square.

        Args:
            square: Board square containing the piece to evaluate.
            color: Player color whose move generation rules should be used.

        Returns:
            Destination squares reachable without enforcing all legality checks, such as whether the
            moving side remains in check. Returns an empty set when no pseudo-legal moves are found.
        """
        ...
