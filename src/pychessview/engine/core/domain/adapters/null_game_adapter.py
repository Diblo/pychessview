# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Provide a fallback game adapter with a minimal, non-validating board state."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...primitives import Piece, PlayerColor
from .protocol import GameAdapterProtocol

if TYPE_CHECKING:
    from ...primitives import Move, Square


class NullGameAdapter(GameAdapterProtocol):
    """Provide a minimal game adapter without move validation or game-state analysis.

    The adapter stores piece placement and FEN strings, but it does not evaluate chess rules.
    Move legality, check state, checkmate state, legal hints, and move history are therefore
    reported as empty or negative results.
    """

    __slots__ = "_default_fen", "_fen", "_pieces"

    _default_fen: str
    _fen: str
    _pieces: dict[Square, Piece]

    def __init__(self, default_fen: str) -> None:
        """Initialize the adapter with the default and current FEN.

        Args:
            default_fen: FEN string used as both the initial default and current position.
        """
        self._default_fen = default_fen
        self._fen = default_fen
        self._pieces = {}

    @property
    def default_fen(self) -> str:
        """Return the stored default FEN string used for future resets.

        Returns:
            The stored default FEN string used for future resets.
        """
        return self._default_fen

    @default_fen.setter
    def default_fen(self, fen: str) -> None:
        """Set the default FEN used for future resets.

        Args:
            fen: FEN string to store as the reset position.
        """
        self._default_fen = fen

    @property
    def fen(self) -> str:
        """Return the stored FEN string for the current position.

        The returned value is not rebuilt from ``_pieces`` and may therefore differ from the manually
        stored piece placement.

        Returns:
            The stored FEN string for the current position.
        """
        return self._fen

    @fen.setter
    def fen(self, fen: str) -> None:
        """Store a FEN string as the current position.

        The null adapter does not parse or apply the FEN. Setting the value only updates
        the stored string and clears any manually stored pieces.

        Args:
            fen: FEN string to store as the current position.
        """
        self._fen = fen
        self._pieces.clear()

    @property
    def turn(self) -> PlayerColor:
        """Return ``PlayerColor.WHITE``.

        The null adapter does not derive the side to move from the stored FEN.

        Returns:
            ``PlayerColor.WHITE``.
        """
        return PlayerColor.WHITE

    def pieces(self) -> dict[Square, Piece]:
        """Return a copy of the manually stored piece placement.

        Returns:
            Mapping of occupied squares to the pieces currently stored on them. The returned mapping is
            independent of the stored FEN string and can be modified without affecting the adapter.
        """
        return dict(self._pieces)

    def piece_at(self, square: Square) -> Piece | None:
        """Return the piece currently stored on a square, if any.

        Args:
            square: Board square to inspect.

        Returns:
            The piece on ``square``, or ``None`` if the square is empty.
        """
        return self._pieces.get(square)

    def set_piece(self, square: Square, piece: Piece | None) -> None:
        """Set or clear the piece stored on a square.

        Args:
            square: Board square to modify.
            piece: Piece to place on ``square``, or ``None`` to clear it.
        """
        if piece is None:
            self._pieces.pop(square, None)
            return
        self._pieces[square] = piece

    def king(self, color: PlayerColor) -> Square | None:
        """Return ``None``.

        The null adapter does not track kings separately and does not inspect the stored
        position for king locations.

        Args:
            color: King color to look up.
        """
        return None

    def is_legal_move(self, move: Move) -> bool:
        """Return ``False``.

        The null adapter does not validate moves against chess rules.

        Args:
            move: Move to validate.

        Returns:
            ``True`` when ``False``; otherwise, ``False``.
        """
        return False

    def is_promotion_move(self, move: Move) -> bool:
        """Return ``False``.

        The null adapter does not analyze moves for promotion conditions.

        Args:
            move: Move to evaluate.

        Returns:
            ``True`` when ``False``; otherwise, ``False``.
        """
        return False

    def has_move_history(self) -> bool:
        """Return ``False``.

        The null adapter does not record move history.

        Returns:
            ``True`` when ``False``; otherwise, ``False``.
        """
        return False

    @property
    def move_history(self) -> tuple[Move, ...]:
        """Return an empty move-history tuple.

        The null adapter does not record applied moves, even when ``move()`` or ``promote()`` updates
        the stored piece placement.

        Returns:
            An empty move-history tuple.
        """
        return tuple()

    def move(self, move: Move) -> None:
        """Move a stored piece from the source square to the destination square.

        No legality checks are performed. If no piece is stored on ``move.from_square``,
        the method leaves the position unchanged.

        Args:
            move: Move to apply.
        """
        piece = self._pieces.pop(move.from_square, None)
        if piece is not None:
            if move.promotion is not None:
                piece = Piece(piece.color, move.promotion)
            self._pieces[move.to_square] = piece

    def is_check(self) -> bool:
        """Return ``False``.

        The null adapter does not evaluate check state.

        Returns:
            ``True`` when ``False``; otherwise, ``False``.
        """
        return False

    def is_checkmate(self) -> bool:
        """Return ``False``.

        The null adapter does not evaluate checkmate state.

        Returns:
            ``True`` when ``False``; otherwise, ``False``.
        """
        return False

    def get_legal_hints(self, square: Square) -> set[Square]:
        """Return an empty set of legal destination squares.

        The null adapter does not calculate legal moves, so the result is always empty even when
        ``square`` contains a piece.

        Args:
            square: Board square whose piece would otherwise be evaluated.

        Returns:
            An empty set of legal destination squares.
        """
        return set()

    def get_pseudo_legal_hints(self, square: Square, color: PlayerColor) -> set[Square]:
        """Return an empty set of pseudo-legal destination squares.

        The null adapter does not calculate pseudo-legal moves, so the result is always empty
        regardless of ``square`` or ``color``.

        Args:
            square: Board square whose piece would otherwise be evaluated.
            color: Player color that would otherwise be used during evaluation.

        Returns:
            An empty set of pseudo-legal destination squares.
        """
        return set()
