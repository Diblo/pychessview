# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Exceptions raised by the pychessview package."""


class ChessboardViewError(Exception):
    """Base exception for chess board view errors."""


class MoveError(ChessboardViewError):
    """Base exception for move operations."""


class StateError(ChessboardViewError):
    """Base exception for board state operations."""


class SquareOccupiedError(StateError):
    """Raised when adding a piece to an occupied square."""


class PieceNotFoundError(StateError):
    """Raised when an operation requires an existing piece, but none is present."""


class ThemeError(ChessboardViewError):
    """Raised when theme content has invalid format or data."""


class ThemeParseError(ThemeError):
    """Raised when theme content has invalid format or data."""


class LayoutError(ChessboardViewError):
    """Raised when layout content has invalid data."""
