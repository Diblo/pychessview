# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for the standard chess factory."""

import pytest

from pychessview.engine.core.domain.adapters.python_chess_adapter import PythonChessGameAdapter
from pychessview.engine.core.primitives import PieceKind, PlayerColor
from pychessview.engine.factory.standard_chess import (
    StandardChessAdapterFactory,
    StandardChessControllerFactory,
    StandardChessFactory,
    StandardChessThemeProvider,
)

pytestmark = [pytest.mark.unit, pytest.mark.requires_python_chess]


def test_standard_chess_factory_builds_spec_with_chess_runtime_parts() -> None:
    """Create a game spec that wires standard chess rules and controller policy.

    The factory is the public construction path for standard chess, so the spec
    must expose python-chess-backed adapters, standard controller creation, and
    color-specific promotion choices.
    """
    spec = StandardChessFactory.create_game_spec()

    assert spec.definition.default_fen.startswith("rnbqkbnr/")
    assert [piece.kind for piece in spec.definition.white_promotion_pieces] == [
        PieceKind.QUEEN,
        PieceKind.ROOK,
        PieceKind.BISHOP,
        PieceKind.KNIGHT,
    ]
    assert all(piece.color is PlayerColor.BLACK for piece in spec.definition.black_promotion_pieces)
    assert isinstance(spec.theme_provider, StandardChessThemeProvider)
    assert isinstance(spec.adapter_factory, StandardChessAdapterFactory)
    assert isinstance(spec.controller_factory, StandardChessControllerFactory)
    assert isinstance(spec.adapter_factory.create_game_adapter(), PythonChessGameAdapter)
