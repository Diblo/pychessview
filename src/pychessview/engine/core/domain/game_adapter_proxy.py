# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Proxy wrapper for game adapters in the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .adapters.protocol import GameAdapterProtocol

if TYPE_CHECKING:
    from ..primitives import Move, Piece, PlayerColor, Square


class GameAdapterProxy(GameAdapterProtocol):
    """Proxy that allows the active game adapter to be swapped."""

    __slots__ = "_impl"

    def __init__(self, impl: GameAdapterProtocol) -> None:
        """Initialize the proxy with the game adapter implementation to delegate game-state calls to.

        Args:
            impl: Value used to initialize ``impl``.
        """
        self._impl = impl

    def switch_adapter(self, impl: GameAdapterProtocol) -> None:
        """Switch the active game adapter.

        Args:
            impl: Implementation instance to delegate to.
        """
        self._impl = impl

    @property
    def default_fen(self) -> str:
        """Default FEN used when resetting the adapter.

        Returns:
            Default FEN used when resetting the adapter.
        """
        return self._impl.default_fen

    @default_fen.setter
    def default_fen(self, fen: str) -> None:
        """Set the default FEN string used for future resets.

        Args:
            fen: FEN string to use when future resets request the adapter default position.
        """
        self._impl.default_fen = fen

    @property
    def fen(self) -> str:
        """Current board position as a FEN string.

        Returns:
            Current board position as a FEN string.
        """
        return self._impl.fen

    @fen.setter
    def fen(self, fen: str) -> None:
        """Replace the current board position using a FEN string.

        Args:
            fen: FEN string describing the position that should become active.
        """
        self._impl.fen = fen

    @property
    def turn(self) -> PlayerColor:
        """Player whose turn it is to move.

        Returns:
            Player whose turn it is to move.
        """
        return self._impl.turn

    @property
    def move_history(self) -> tuple[Move, ...]:
        """Recorded move history for the current game state.

        Returns:
            Recorded move history for the current game state.
        """
        return self._impl.move_history

    def pieces(self) -> dict[Square, Piece]:
        """Return the current piece placement as a mapping from occupied squares to pieces.

        Returns:
            Mapping of occupied squares to their pieces.
        """
        return self._impl.pieces()

    def piece_at(self, square: Square) -> Piece | None:
        """Return the piece currently placed on the given square, if any.

        Args:
            square: Square to inspect.

        Returns:
            The piece on ``square``, or ``None`` when the square is empty.
        """
        return self._impl.piece_at(square)

    def set_piece(self, square: Square, piece: Piece | None) -> None:
        """Place a piece on the given square or clear the square when ``piece`` is ``None``.

        Args:
            square: Square to update.
            piece: Piece to place on ``square``, or ``None`` to clear it.
        """
        self._impl.set_piece(square, piece)

    def king(self, color: PlayerColor) -> Square | None:
        """Return the square occupied by the specified color's king, if present.

        Args:
            color: Player color whose king square should be queried.

        Returns:
            The king square for ``color``, or ``None`` when no king is present.
        """
        return self._impl.king(color)

    def is_legal_move(self, move: Move) -> bool:
        """Return whether ``move`` is legal in the current position.

        Args:
            move: Move to validate against the current position.

        Returns:
            ``True`` when the delegated adapter accepts ``move`` as legal.
        """
        return self._impl.is_legal_move(move)

    def is_promotion_move(self, move: Move) -> bool:
        """Return whether ``move`` requires a promotion choice.

        Args:
            move: Move to inspect for promotion handling.

        Returns:
            ``True`` when ``move`` reaches a promotion rank and needs a promotion piece.
        """
        return self._impl.is_promotion_move(move)

    def has_move_history(self) -> bool:
        """Return whether at least one move has been played.

        Returns:
            ``True`` when the delegated adapter has recorded at least one played move.
        """
        return self._impl.has_move_history()

    def move(self, move: Move) -> None:
        """Apply a move to the current state.

        Args:
            move: Move to apply to the delegated adapter.
        """
        self._impl.move(move)

    def is_check(self) -> bool:
        """Return whether the side to move is currently in check.

        Returns:
            ``True`` when the delegated adapter reports the side to move as in check.
        """
        return self._impl.is_check()

    def is_checkmate(self) -> bool:
        """Return whether the current position is checkmate.

        Returns:
            ``True`` when the delegated adapter reports the current position as checkmate.
        """
        return self._impl.is_checkmate()

    def get_legal_hints(self, square: Square) -> set[Square]:
        """Return the legal destination squares for the piece on the given square.

        Args:
            square: Square whose legal destination squares should be computed.

        Returns:
            Legal destination squares for the piece on ``square``.
        """
        return self._impl.get_legal_hints(square)

    def get_pseudo_legal_hints(self, square: Square, color: PlayerColor) -> set[Square]:
        """Return pseudo-legal destination squares for the piece on the given square.

        Args:
            square: Square whose pseudo-legal destination squares should be computed.
            color: Player color perspective to use for pseudo-legal move generation.

        Returns:
            Pseudo-legal destination squares for the piece on ``square``.
        """
        return self._impl.get_pseudo_legal_hints(square, color)
