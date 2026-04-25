# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Provide a game adapter backed by the python-chess board implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import chess

from ...primitives import PIECES, SQUARES, Move, PieceKind, PlayerColor, Rank
from .protocol import GameAdapterProtocol

if TYPE_CHECKING:
    from ...primitives import Piece, Square

_COLOR_TO_CHESS_COLOR: dict[PlayerColor, chess.Color] = {PlayerColor.WHITE: chess.WHITE, PlayerColor.BLACK: chess.BLACK}

_KIND_TO_CHESS_TYPE: dict[PieceKind, chess.PieceType] = {
    PieceKind.KING: chess.KING,
    PieceKind.QUEEN: chess.QUEEN,
    PieceKind.ROOK: chess.ROOK,
    PieceKind.BISHOP: chess.BISHOP,
    PieceKind.KNIGHT: chess.KNIGHT,
    PieceKind.PAWN: chess.PAWN,
}

_CHESS_TYPE_TO_KIND: dict[chess.PieceType, PieceKind] = {
    chess_type: kind for kind, chess_type in _KIND_TO_CHESS_TYPE.items()
}

_PIECE_TO_CHESS_PIECE: dict[Piece, chess.Piece] = {
    piece: chess.Piece(_KIND_TO_CHESS_TYPE[piece.kind], _COLOR_TO_CHESS_COLOR[piece.color]) for piece in PIECES
}

_CHESS_PIECE_TO_PIECE: dict[chess.Piece, Piece] = {
    chess_piece: piece for piece, chess_piece in _PIECE_TO_CHESS_PIECE.items()
}


def _move_to_chess_move(move: Move) -> chess.Move:
    """Convert a core move into a python-chess move.

    Args:
        move: Move involved in the operation.

    Returns:
        Convert a core move into a python-chess move.
    """
    promotion = None
    if move.promotion is not None:
        promotion = _KIND_TO_CHESS_TYPE[move.promotion]
    return chess.Move(move.from_square.index, move.to_square.index, promotion=promotion)


def _chess_move_to_move(move: chess.Move) -> Move:
    """Convert a python-chess move into a core move.

    Args:
        move: Move involved in the operation.

    Returns:
        Convert a python-chess move into a core move.
    """
    promotion = None
    if move.promotion is not None:
        promotion = _CHESS_TYPE_TO_KIND[move.promotion]
    return Move(SQUARES[move.from_square], SQUARES[move.to_square], promotion)


class PythonChessGameAdapter(GameAdapterProtocol):
    """Provide a game adapter that delegates board state and rule handling to python-chess."""

    __slots__ = "_board", "_default_fen"

    _board: chess.Board
    _default_fen: str

    def __init__(self, default_fen: str, board: chess.Board | None = None) -> None:
        """Initialize the adapter from a default FEN and an optional python-chess board.

        Args:
            default_fen: FEN string used as the default position for future resets.
            board: Existing python-chess board to wrap. When omitted, a new board is created
                and initialized from ``default_fen``.
        """
        self.default_fen = default_fen
        if board is None:
            self._board = chess.Board()
            self.fen = default_fen
            return

        self._board = board

    @property
    def default_fen(self) -> str:
        """Return the default FEN string used when resetting the wrapped board.

        Returns:
            The default FEN string used when resetting the wrapped board.
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
        """Return the current python-chess board state as a FEN string.

        Returns:
            The current python-chess board state as a FEN string.
        """
        return self._board.fen()

    @fen.setter
    def fen(self, fen: str) -> None:
        """Replace the current board position from a FEN string.

        Full FEN strings update the complete board state. Piece-placement-only FEN strings
        update only the board layout.

        Args:
            fen: FEN string describing the position to load.
        """
        if " " in fen:
            self._board.set_fen(fen)
            return
        self._board.set_board_fen(fen)

    @property
    def turn(self) -> PlayerColor:
        """Return the color of the player whose turn it is to move.

        Returns:
            The color of the player whose turn it is to move.
        """
        return PlayerColor.WHITE if self._board.turn == chess.WHITE else PlayerColor.BLACK

    def pieces(self) -> dict[Square, Piece]:
        """Return the current piece placement derived from the wrapped python-chess board.

        Returns:
            Mapping containing only occupied squares. The result is a fresh mapping built from the
            board state at call time.
        """
        return {
            SQUARES[square_index]: _CHESS_PIECE_TO_PIECE[chess_piece]
            for square_index, chess_piece in self._board.piece_map().items()
        }

    def piece_at(self, square: Square) -> Piece | None:
        """Return the piece currently placed on a square, if any.

        Args:
            square: Board square to inspect.

        Returns:
            The piece on ``square``, or ``None`` if the square is empty.
        """
        chess_piece = self._board.piece_at(square.index)
        if chess_piece is None:
            return None
        return _CHESS_PIECE_TO_PIECE[chess_piece]

    def set_piece(self, square: Square, piece: Piece | None) -> None:
        """Set or clear the piece on a square.

        Args:
            square: Board square to modify.
            piece: Piece to place on ``square``, or ``None`` to clear it.
        """
        chess_piece = None if piece is None else _PIECE_TO_CHESS_PIECE[piece]
        self._board.set_piece_at(square.index, chess_piece)

    def king(self, color: PlayerColor) -> Square | None:
        """Return the square occupied by the specified king, if present.

        Args:
            color: Color of the king to locate.

        Returns:
            Square occupied by the king of ``color``, or ``None`` if no such king is present.
        """
        king_square = self._board.king(_COLOR_TO_CHESS_COLOR[color])
        return SQUARES[king_square] if king_square is not None else None

    def is_legal_move(self, move: Move) -> bool:
        """Return whether a move is legal in the current position.

        Promotion moves are only considered legal when ``move.promotion`` provides a valid
        non-pawn, non-king piece kind.

        Args:
            move: Move to validate.

        Returns:
            ``True`` if ``move`` is legal in the current position; otherwise, ``False``.
        """
        if self.piece_at(move.from_square) is None:
            return False

        if self.is_promotion_move(move) != (move.promotion is not None):
            return False

        if move.promotion is not None:
            if move.promotion in (PieceKind.KING, PieceKind.PAWN):
                return False

        return self._board.is_legal(_move_to_chess_move(move))

    def is_promotion_move(self, move: Move) -> bool:
        """Return whether a move requires a promotion choice.

        A move is treated as a promotion move when a pawn moves to the back rank for its color.

        Args:
            move: Move to evaluate.

        Returns:
            ``True`` if ``move`` requires promotion; otherwise, ``False``.
        """
        piece = self.piece_at(move.from_square)
        if piece is None:
            return False

        return piece.kind is PieceKind.PAWN and (
            (move.to_square.rank == Rank.EIGHT and piece.color == PlayerColor.WHITE)
            or (move.to_square.rank == Rank.ONE and piece.color == PlayerColor.BLACK)
        )

    def has_move_history(self) -> bool:
        """Return whether at least one move has been recorded.

        Returns:
            ``True`` if at least one move has been pushed onto the board move stack; otherwise, ``False``.
        """
        return bool(self._board.move_stack)

    @property
    def move_history(self) -> tuple[Move, ...]:
        """Return the move history converted from the wrapped python-chess move stack.

        Returns:
            The move history converted from the wrapped python-chess move stack.
        """
        return tuple(_chess_move_to_move(move) for move in self._board.move_stack)

    def move(self, move: Move) -> None:
        """Apply a move to the current game state.

        The move is forwarded directly to the wrapped python-chess board without additional adapter-
        level validation.

        Args:
            move: Move to apply.
        """
        self._board.push(_move_to_chess_move(move))

    def is_check(self) -> bool:
        """Return whether the side to move is currently in check.

        Returns:
            ``True`` if the side to move is in check; otherwise, ``False``.
        """
        return self._board.is_check()

    def is_checkmate(self) -> bool:
        """Return whether the current position is checkmate.

        Returns:
            ``True`` if the side to move is checkmated; otherwise, ``False``.
        """
        return self._board.is_checkmate()

    def get_legal_hints(self, square: Square) -> set[Square]:
        """Return legal destination squares for the piece on a square.

        Args:
            square: Board square containing the piece to evaluate.

        Returns:
            Destination squares reachable by legal moves from ``square``. Returns an empty set when
            the square is empty or when the piece has no legal moves.
        """
        from_mask = chess.BB_SQUARES[square.index]
        return set(SQUARES[move.to_square] for move in self._board.generate_legal_moves(from_mask=from_mask))

    def get_pseudo_legal_hints(self, square: Square, color: PlayerColor) -> set[Square]:
        """Return pseudo-legal destination squares for the piece on a square.

        The move generation is evaluated from the perspective of ``color``. When ``color`` differs
        from the board turn, a temporary board copy is used with the turn adjusted so hint generation
        can be queried for either side.

        Args:
            square: Board square containing the piece to evaluate.
            color: Player color used when evaluating pseudo-legal moves.

        Returns:
            Destination squares reachable from ``square`` without enforcing all legality checks.
            Returns an empty set when no pseudo-legal moves are found.
        """
        target_turn = _COLOR_TO_CHESS_COLOR[color]
        if self._board.turn == target_turn:
            board = self._board
        else:
            board = self._board.copy(stack=False)
            board.turn = target_turn

        from_mask = chess.BB_SQUARES[square.index]
        return set(SQUARES[move.to_square] for move in board.generate_pseudo_legal_moves(from_mask=from_mask))
