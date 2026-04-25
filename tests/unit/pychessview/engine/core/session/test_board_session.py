# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for board session orchestration."""

from __future__ import annotations

from typing import Any, cast

import pytest

from pychessview.engine.core.annotation_types import CircleType
from pychessview.engine.core.domain.game_spec import GameDefinition, GameSpec
from pychessview.engine.core.primitives import Piece, PieceKind, PlayerColor, Square
from pychessview.engine.core.session.board_session import BoardSession
from pychessview.engine.interaction.controller_event_result import ControllerEventResult
from pychessview.engine.interaction.input.mouse_buttons import MouseButton
from pychessview.engine.layout.primitives import Coord

from ..._helpers import (
    AdapterFactorySpy,
    BoardSessionControllerSpy,
    ControllerFactorySpy,
    ThemeProviderSpy,
    build_board_session_components,
)

pytestmark = pytest.mark.unit


def test_board_session_controller_enabled_switches_between_game_and_null_controller() -> None:
    """Switch the controller proxy target without exposing the proxy internals."""
    components, _, _, _ = build_board_session_components()
    session = BoardSession(components)
    coord = Coord(1, 2)

    game_result = session.controller.on_press(coord, MouseButton.LEFT)
    session.controller_enabled = False
    null_result = session.controller.on_press(coord, MouseButton.LEFT)
    session.controller_enabled = True
    restored_game_result = session.controller.on_press(coord, MouseButton.LEFT)

    assert game_result == ControllerEventResult(handled=True, requires_render=True)
    assert null_result == ControllerEventResult(handled=True, requires_render=False)
    assert restored_game_result == game_result


def test_board_session_load_game_replaces_theme_adapter_controller_and_game_options() -> None:
    """Apply a new game specification through the existing session collaborators."""
    components, game_adapter, theme, promotion_session = build_board_session_components()
    session = BoardSession(components)
    new_controller = BoardSessionControllerSpy("game")
    replacement_theme = object()
    replacement_adapter = object()
    white_override = (Piece(PlayerColor.WHITE, PieceKind.ROOK),)
    black_default = (Piece(PlayerColor.BLACK, PieceKind.QUEEN),)
    adapter_factory = AdapterFactorySpy(replacement_adapter)
    controller_factory = ControllerFactorySpy(new_controller)
    spec = GameSpec(
        GameDefinition("default fen", (Piece(PlayerColor.WHITE, PieceKind.QUEEN),), black_default),
        cast(Any, ThemeProviderSpy(replacement_theme)),
        cast(Any, adapter_factory),
        cast(Any, controller_factory),
    )
    components.highlight_state.set_selected(cast(Any, "player"), Square(0, 0))
    components.highlight_state.set_check(Square(4, 0))
    components.annotation_state.add_circle(CircleType.PRIMARY, Square(0, 0))

    session.load_game(
        spec,
        player=PlayerColor.BLACK,
        default_fen="override fen",
        white_promotion_pieces=white_override,
    )

    assert components.view_state.player is PlayerColor.BLACK
    assert theme.load_calls == [replacement_theme]
    assert promotion_session.white_options == [white_override]
    assert promotion_session.black_options == [black_default]
    assert adapter_factory.default_fen_calls == ["override fen"]
    assert game_adapter.switched_adapters == [replacement_adapter]
    assert controller_factory.calls == [
        (
            components.view_state,
            components.game_session,
            components.interaction_session,
            components.annotation_session,
            components.promotion_session,
            components.query,
        )
    ]
    assert session.controller.on_press(Coord(3, 4), MouseButton.LEFT) is new_controller.result
    assert components.highlight_state.get_selected() is None
    assert components.highlight_state.get_check() is None
    assert components.annotation_state.has_annotation() is False
