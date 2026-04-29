# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Core value objects and enums for the pychessview package.

Constants:
    PIECES: Tuple containing one instance of each supported colored chess piece.
    SQUARES: List containing the 64 squares in board-index order.
"""

from __future__ import annotations

from enum import IntEnum, StrEnum
from typing import TYPE_CHECKING, overload

if TYPE_CHECKING:
    from typing import Final


class PlayerColor(StrEnum):
    """Enumeration of supported player colors.

    Attributes:
        WHITE: White player color.
        BLACK: Black player color.
        text: Text value associated with the enum member.
        symbol: Short symbol associated with the enum member.
    """

    WHITE = ("white", "w")
    BLACK = ("black", "b")
    text: str
    symbol: str

    def __new__(cls, text: str, symbol: str) -> PlayerColor:
        """Create a player color member from its raw values.

        Args:
            text: Text value to store or display.
            symbol: Value used to initialize ``symbol``.

        Returns:
            A player color member from its raw values.
        """
        obj = str.__new__(cls, text)
        obj._value_ = text
        obj.text = text
        obj.symbol = symbol
        return obj

    @property
    def opposite(self) -> PlayerColor:
        """Opposite player color.

        Returns:
            Opposite player color.
        """
        return PlayerColor.BLACK if self == PlayerColor.WHITE else PlayerColor.WHITE


class PieceKind(StrEnum):
    """Enumeration of supported chess piece kinds.

    Attributes:
        KING: King piece kind.
        QUEEN: Queen piece kind.
        ROOK: Rook piece kind.
        BISHOP: Bishop piece kind.
        KNIGHT: Knight piece kind.
        PAWN: Pawn piece kind.
        text: Text value associated with the enum member.
        symbol: Short symbol associated with the enum member.
        order: Ordering value associated with the enum member.
    """

    KING = ("king", "k", 6)
    QUEEN = ("queen", "q", 5)
    ROOK = ("rook", "r", 4)
    BISHOP = ("bishop", "b", 3)
    KNIGHT = ("knight", "n", 2)
    PAWN = ("pawn", "p", 1)

    text: str
    symbol: str
    order: int

    def __new__(cls, text: str, symbol: str, order: int) -> PieceKind:
        """Create a piece kind member from its raw values.

        Args:
            text: Text value to store or display.
            symbol: Value used to initialize ``symbol``.
            order: Value used to initialize ``order``.

        Returns:
            A piece kind member from its raw values.
        """
        obj = str.__new__(cls, text)
        obj._value_ = text
        obj.text = text
        obj.symbol = symbol
        obj.order = order
        return obj

    @classmethod
    def from_symbol(cls, symbol: str) -> PieceKind:
        """Return the enum member associated with the given symbol.

        Args:
            symbol: Single-letter piece symbol such as ``"k"`` or ``"n"``.

        Returns:
            The enum member that uses ``symbol``.
        """
        kind = _SYMBOL_TO_KIND.get(symbol)
        if kind is None:
            raise ValueError(f"Symbol must be k, q, r, b, n, or p, got '{symbol}'")
        return kind


_SYMBOL_TO_KIND: dict[str, PieceKind] = {kind.symbol: kind for kind in PieceKind}


class Piece:
    """Represents a colored chess piece.

    Attributes:
        color: Color value associated with the object.
        kind: Piece kind associated with the object.
        symbol: Short symbol associated with the object.
        order: Ordering value associated with the object.
    """

    __slots__ = "color", "kind", "symbol", "order"

    color: Final[PlayerColor]
    kind: Final[PieceKind]
    symbol: Final[str]
    order: Final[int]

    def __init__(self, color: PlayerColor, kind: PieceKind) -> None:
        """Initialize the piece with its initial configuration.

        Args:
            color: Color value associated with the object or operation.
            kind: Value used to initialize ``kind``.
        """
        self.color = color
        self.kind = kind
        self.symbol = kind.symbol.upper() if color == PlayerColor.WHITE else kind.symbol
        self.order = kind.order

    @classmethod
    def from_symbol(cls, symbol: str) -> Piece:
        """Return the enum member associated with the given symbol.

        Args:
            symbol: Single-letter piece symbol, using uppercase for white and lowercase for black.

        Returns:
            The enum member that uses ``symbol``.
        """
        if symbol.isupper():
            color = PlayerColor.WHITE
        else:
            color = PlayerColor.BLACK

        return Piece(color, PieceKind.from_symbol(symbol.lower()))

    def __eq__(self, other: object) -> bool:
        """Return whether ``other`` represents the same value as this instance.

        Args:
            other: Object to compare against this instance.

        Returns:
            ``True`` when ``other`` represents the same value as this instance; otherwise, ``False``.
        """
        if not isinstance(other, Piece):
            return False
        return self.color is other.color and self.kind is other.kind

    def __hash__(self) -> int:
        """Return a hash value for the instance.

        Returns:
            Hash value for the instance.
        """
        return hash((self.color, self.kind))

    def __str__(self) -> str:
        """Return a human-readable representation of the instance.

        Returns:
            Human-readable representation of the instance.
        """
        return f"{str(self.color)} {str(self.kind)}"

    def __repr__(self) -> str:
        """Return a developer-oriented representation of the instance.

        Returns:
            Developer-oriented representation of the instance.
        """
        return f"Piece(color={repr(self.color)}, kind={repr(self.kind)}, symbol='{self.symbol}', order={self.order})"


PIECES = tuple(Piece(color, kind) for color in PlayerColor for kind in PieceKind)
"""Tuple containing one instance of each supported colored chess piece."""


class File(IntEnum):
    """Enumeration of board file indices.

    Attributes:
        A: File A.
        B: File B.
        C: File C.
        D: File D.
        E: File E.
        F: File F.
        G: File G.
        H: File H.
        VALUE: Numeric value associated with the enum member.
        text: Text value associated with the enum member.
    """

    A = (0, "A")
    B = (1, "B")
    C = (2, "C")
    D = (3, "D")
    E = (4, "E")
    F = (5, "F")
    G = (6, "G")
    H = (7, "H")

    text: str

    def __new__(cls, index: int, text: str) -> File:
        """Create a file member from its raw values.

        Args:
            index: Zero-based index associated with the created object.
            text: Text value to store or display.

        Returns:
            A file member from its raw values.
        """
        obj = int.__new__(cls, index)
        obj._value_ = index
        obj.text = text
        return obj

    @classmethod
    def from_axis(cls, index: int) -> File:
        """Return the enum member for the given zero-based board axis index.

        Args:
            index: Zero-based file index in the range ``0`` through ``7``.

        Returns:
            The enum member for ``index``.
        """
        file = _INDEX_TO_FILE.get(index)
        if file is None:
            raise ValueError(f"file index must be in [0, 7], got {index}")
        return file

    def __str__(self) -> str:
        """Return a human-readable representation of the instance.

        Returns:
            Human-readable representation of the instance.
        """
        return f"file {self.name}"

    def __repr__(self) -> str:
        """Return a developer-oriented representation of the instance.

        Returns:
            Developer-oriented representation of the instance.
        """
        return f"File({self.name}=({self.value}, '{self.text}'))"


_INDEX_TO_FILE: dict[int, File] = {file.value: file for file in File}


class Rank(IntEnum):
    """Enumeration of board rank indices.

    Attributes:
        ONE: Rank one.
        TWO: Rank two.
        THREE: Rank three.
        FOUR: Rank four.
        FIVE: Rank five.
        SIX: Rank six.
        SEVEN: Rank seven.
        EIGHT: Rank eight.
        VALUE: Numeric value associated with the enum member.
        text: Text value associated with the enum member.
    """

    ONE = (0, "1")
    TWO = (1, "2")
    THREE = (2, "3")
    FOUR = (3, "4")
    FIVE = (4, "5")
    SIX = (5, "6")
    SEVEN = (6, "7")
    EIGHT = (7, "8")

    text: str

    def __new__(cls, index: int, text: str) -> Rank:
        """Create a rank member from its raw values.

        Args:
            index: Zero-based index associated with the created object.
            text: Text value to store or display.

        Returns:
            A rank member from its raw values.
        """
        obj = int.__new__(cls, index)
        obj._value_ = index
        obj.text = text
        return obj

    @classmethod
    def from_axis(cls, index: int) -> Rank:
        """Return the enum member for the given zero-based board axis index.

        Args:
            index: Zero-based rank index in the range ``0`` through ``7``.

        Returns:
            The enum member for ``index``.
        """
        rank = _INDEX_TO_RANK.get(index)
        if rank is None:
            raise ValueError(f"rank index must be in [0, 7], got {index}")
        return rank

    def __str__(self) -> str:
        """Return a human-readable representation of the instance.

        Returns:
            Human-readable representation of the instance.
        """
        return f"rank {self.value}"

    def __repr__(self) -> str:
        """Return a developer-oriented representation of the instance.

        Returns:
            Developer-oriented representation of the instance.
        """
        return f"Rank({self.name}=({self.value}, '{self.text}'))"


_INDEX_TO_RANK: dict[int, Rank] = {rank.value: rank for rank in Rank}


class Square:
    """Represents a square on the pychessview.

    Attributes:
        file: Board file associated with the object.
        rank: Board rank associated with the object.
        index: Zero-based board index associated with the object.
    """

    __slots__ = "file", "rank", "index"

    file: Final[File]
    rank: Final[Rank]
    index: Final[int]

    @overload
    def __init__(self, file: File, rank: Rank) -> None: ...
    @overload
    def __init__(self, file: int, rank: int) -> None: ...
    def __init__(self, file: File | int, rank: Rank | int) -> None:
        """Initialize the square with its initial configuration.

        Args:
            file: Board file associated with the object.
            rank: Board rank associated with the object.
        """
        if not isinstance(file, File):
            file = File.from_axis(file)
        if not isinstance(rank, Rank):
            rank = Rank.from_axis(rank)

        self.file = file
        self.rank = rank
        self.index = rank * 8 + file

    def is_light(self) -> bool:
        """Return whether the square is light-colored.

        Returns:
            ``True`` when the condition is met; otherwise, ``False``.
        """
        return not (self.file + self.rank) % 2 == 0

    def rotated(self) -> Square:
        """Return the square rotated 180 degrees around the board center.

        Returns:
            The square on the opposite side of the board.
        """
        return Square(File.H - self.file, Rank.EIGHT - self.rank)

    @classmethod
    def from_index(cls, index: int) -> Square:
        """Return the square for the given zero-based board index.

        Args:
            index: Zero-based square index in board order, from ``0`` for ``A1`` to ``63`` for ``H8``.

        Returns:
            The square corresponding to ``index``.
        """
        if not 0 <= index <= 63:
            raise ValueError(f"index must be in [0, 63], got {index}")
        rank, file = divmod(index, 8)
        return cls(file=file, rank=rank)

    def __eq__(self, other: object) -> bool:
        """Return whether ``other`` represents the same value as this instance.

        Args:
            other: Object to compare against this instance.

        Returns:
            ``True`` when ``other`` represents the same value as this instance; otherwise, ``False``.
        """
        if not isinstance(other, Square):
            return False
        return self.index == other.index

    def __hash__(self) -> int:
        """Return a hash value for the instance.

        Returns:
            Hash value for the instance.
        """
        return self.index

    def __str__(self) -> str:
        """Return a human-readable representation of the instance.

        Returns:
            Human-readable representation of the instance.
        """
        return f"{str(self.file)} {str(self.rank)}"

    def __repr__(self) -> str:
        """Return a developer-oriented representation of the instance.

        Returns:
            Developer-oriented representation of the instance.
        """
        return f"Square(file={repr(self.file)}, rank={repr(self.rank)}, index={self.index})"


SQUARES = [Square.from_index(index) for index in range(64)]
"""List containing the 64 squares in board-index order."""


class Squares:
    """Named constants for the 64 squares, in board order."""

    (
        A1,
        B1,
        C1,
        D1,
        E1,
        F1,
        G1,
        H1,
        A2,
        B2,
        C2,
        D2,
        E2,
        F2,
        G2,
        H2,
        A3,
        B3,
        C3,
        D3,
        E3,
        F3,
        G3,
        H3,
        A4,
        B4,
        C4,
        D4,
        E4,
        F4,
        G4,
        H4,
        A5,
        B5,
        C5,
        D5,
        E5,
        F5,
        G5,
        H5,
        A6,
        B6,
        C6,
        D6,
        E6,
        F6,
        G6,
        H6,
        A7,
        B7,
        C7,
        D7,
        E7,
        F7,
        G7,
        H7,
        A8,
        B8,
        C8,
        D8,
        E8,
        F8,
        G8,
        H8,
    ) = SQUARES


class SquareData:
    """Pairs a square with the piece currently on it.

    Attributes:
        square: Board square associated with the object.
        piece: Chess piece associated with the object.
    """

    __slots__ = "square", "piece"

    square: Final[Square]
    piece: Final[Piece]

    def __init__(self, square: Square, piece: Piece) -> None:
        """Initialize the square data with its initial configuration.

        Args:
            square: Board square associated with the object or operation.
            piece: Piece value associated with the object or operation.
        """
        self.square = square
        self.piece = piece

    def is_player_piece(self, color: PlayerColor) -> bool:
        """Return whether the stored piece belongs to ``color``.

        Args:
            color: Player color to compare against the stored piece.

        Returns:
            ``True`` when the stored piece has the requested color.
        """
        return self.piece.color == color

    def __eq__(self, other: object) -> bool:
        """Return whether ``other`` represents the same value as this instance.

        Args:
            other: Object to compare against this instance.

        Returns:
            ``True`` when ``other`` represents the same value as this instance; otherwise, ``False``.
        """
        if not isinstance(other, SquareData):
            return False
        return self.square == other.square and self.piece == other.piece

    def __str__(self) -> str:
        """Return a human-readable representation of the instance.

        Returns:
            Human-readable representation of the instance.
        """
        return f"square {self.square.file.text}{self.square.rank.value} with {str(self.piece)}"

    def __repr__(self) -> str:
        """Return a developer-oriented representation of the instance.

        Returns:
            Developer-oriented representation of the instance.
        """
        return f"SquareData(square={str(self.square)}, piece={str(self.piece)})"


class Move:
    """Represents a move from one square to another.

    Attributes:
        from_square: Origin square for the move.
        to_square: Destination square for the move.
        promotion: Optional piece kind to promote to, or ``None`` if not applicable.
    """

    __slots__ = "from_square", "to_square", "promotion"

    from_square: Final[Square]
    to_square: Final[Square]
    promotion: Final[PieceKind | None]

    def __init__(self, from_square: Square, to_square: Square, promotion: PieceKind | None = None) -> None:
        """Initialize the move with its initial configuration.

        Args:
            from_square: Value used to initialize ``from_square``.
            to_square: Value used to initialize ``to_square``.
            promotion: Optional piece kind to promote to, or ``None`` if not applicable.
        """
        if not 0 <= from_square.index <= 63:
            raise ValueError(f"from_ must be in [0, 63], got {from_square}")
        if not 0 <= to_square.index <= 63:
            raise ValueError(f"to must be in [0, 63], got {to_square}")

        self.from_square = from_square
        self.to_square = to_square
        self.promotion = promotion

    def with_promotion(self, promotion: PieceKind) -> Move:
        """Return a copy of this move with the given promotion piece kind.

        Args:
            promotion: Piece kind to promote to.

        Returns:
            A copy of this move with the given promotion piece kind.
        """
        return Move(self.from_square, self.to_square, promotion)

    def __eq__(self, other: object) -> bool:
        """Return whether ``other`` represents the same value as this instance.

        Args:
            other: Object to compare against this instance.

        Returns:
            ``True`` when ``other`` represents the same value as this instance; otherwise, ``False``.
        """
        if not isinstance(other, Move):
            return False
        return (
            self.from_square == other.from_square
            and self.to_square == other.to_square
            and self.promotion == other.promotion
        )

    def __str__(self) -> str:
        """Return a human-readable representation of the instance.

        Returns:
            Human-readable representation of the instance.
        """
        return f"move from {str(self.from_square)} to {str(self.to_square)} with promotion {str(self.promotion)}"

    def __repr__(self) -> str:
        """Return a developer-oriented representation of the instance.

        Returns:
            Developer-oriented representation of the instance.
        """
        return (
            f"Move(from_square={repr(self.from_square)}, to_square={repr(self.to_square)}, "
            f"promotion={repr(self.promotion)})"
        )
