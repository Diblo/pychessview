# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for game specification value objects."""

from __future__ import annotations

from typing import cast

import pytest

from pychessview.engine.core.domain.game_spec import (
    ControllerFactoryProtocol,
    GameAdapterFactoryProtocol,
    GameDefinition,
    GameSpec,
    ThemeProviderProtocol,
)
from pychessview.engine.core.primitives import Piece, PieceKind, PlayerColor

pytestmark = pytest.mark.unit


def test_game_definition_exposes_default_position_and_promotion_options() -> None:
    """Store the immutable game defaults used when board sessions are built or reset."""
    white_piece = Piece(PlayerColor.WHITE, PieceKind.QUEEN)
    black_piece = Piece(PlayerColor.BLACK, PieceKind.QUEEN)

    definition = GameDefinition("default fen", (white_piece,), (black_piece,))

    assert definition.default_fen == "default fen"
    assert definition.white_promotion_pieces == (white_piece,)
    assert definition.black_promotion_pieces == (black_piece,)


def test_game_definition_compares_and_hashes_by_value() -> None:
    """Treat equivalent game defaults as the same value in caches and assertions."""
    piece = Piece(PlayerColor.WHITE, PieceKind.ROOK)

    definition = GameDefinition("fen", (piece,), ())

    assert definition == GameDefinition("fen", (piece,), ())
    assert definition != GameDefinition("other", (piece,), ())
    assert definition != object()
    assert hash(definition) == hash(GameDefinition("fen", (piece,), ()))
    assert repr(definition) == (
        f"GameDefinition(default_fen='fen', white_promotion_pieces={(piece,)!r}, black_promotion_pieces=())"
    )


def test_game_spec_groups_runtime_factories_without_copying_them() -> None:
    """Keep factory identity intact because board-session construction calls these collaborators later."""
    definition = GameDefinition("fen", (), ())
    theme_provider = cast(ThemeProviderProtocol, object())
    adapter_factory = cast(GameAdapterFactoryProtocol, object())
    controller_factory = cast(ControllerFactoryProtocol, object())

    spec = GameSpec(definition, theme_provider, adapter_factory, controller_factory)

    assert spec.definition is definition
    assert spec.theme_provider is theme_provider
    assert spec.adapter_factory is adapter_factory
    assert spec.controller_factory is controller_factory


def test_game_spec_compares_and_hashes_by_collaborator_identity() -> None:
    """Use the configured factories as part of the game-spec value contract."""
    definition = GameDefinition("fen", (), ())
    theme_provider = cast(ThemeProviderProtocol, object())
    adapter_factory = cast(GameAdapterFactoryProtocol, object())
    controller_factory = cast(ControllerFactoryProtocol, object())

    spec = GameSpec(definition, theme_provider, adapter_factory, controller_factory)

    assert spec == GameSpec(definition, theme_provider, adapter_factory, controller_factory)
    assert spec != GameSpec(definition, cast(ThemeProviderProtocol, object()), adapter_factory, controller_factory)
    assert spec != object()
    assert hash(spec) == hash(GameSpec(definition, theme_provider, adapter_factory, controller_factory))
    assert repr(spec).startswith("GameSpec(definition=GameDefinition(")
