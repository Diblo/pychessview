# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for the public View facade."""

from __future__ import annotations

from typing import cast

import pytest

from pychessview.engine.core.domain.game_spec import GameSpec
from pychessview.engine.core.primitives import PlayerColor
from pychessview.engine.layout.primitives import Viewport
from pychessview.engine.render.renderer.protocol import RendererProtocol
from pychessview.engine.theme.theme import Theme
from pychessview.engine.view import View

from ._helpers import (
    ViewBoardSessionBuilderStub,
    ViewBoardSessionStub,
    ViewRendererSpy,
    create_fake_view,
    install_fake_view_runtime,
)

pytestmark = pytest.mark.unit


def test_view_constructor_builds_board_session_from_viewport_and_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    """Create the board session through the builder without assembling the real runtime in this unit test."""
    renderer = ViewRendererSpy()
    game_spec = cast(GameSpec, object())
    install_fake_view_runtime(monkeypatch)

    view = View(
        cast(RendererProtocol, renderer),
        game_spec,
        width=320,
        height=240,
        x=7,
        y=8,
        player=PlayerColor.BLACK,
        default_fen="fen",
    )

    assert view is not None
    assert len(ViewBoardSessionStub.instances) == 1
    assert ViewBoardSessionBuilderStub.calls == [
        (
            renderer,
            game_spec,
            Viewport(7, 8, 320, 240),
            {
                "player": PlayerColor.BLACK,
                "default_fen": "fen",
                "white_promotion_pieces": None,
                "black_promotion_pieces": None,
                "game_session_class": None,
                "interaction_session_class": None,
                "annotation_session_class": None,
                "promotion_session_class": None,
            },
        )
    ]


def test_view_delegates_public_properties_and_mutators_to_session(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep View as a facade over BoardSession rather than duplicating session state."""
    view, _, game_spec, session = create_fake_view(monkeypatch)
    replacement_theme = cast(Theme, object())

    view.theme = replacement_theme
    view.controller_enabled = False
    view.load_game(game_spec, player=PlayerColor.BLACK, default_fen="other fen")
    view.load_position_from_fen("position fen")
    view.reset_board("reset fen")

    assert view.theme is session.theme
    assert session.theme.load_calls == [replacement_theme]
    assert view.settings is session.view_state
    assert view.fen == "current fen"
    assert view.game is session.game_session
    assert view.interaction is session.interaction_session
    assert view.annotation is session.annotation_session
    assert view.query is session.query
    assert view.controller is session.controller
    assert view.controller_enabled is False
    assert session.load_game_calls == [
        (
            game_spec,
            {
                "player": PlayerColor.BLACK,
                "default_fen": "other fen",
                "white_promotion_pieces": None,
                "black_promotion_pieces": None,
            },
        )
    ]
    assert session.game_session.load_fen_calls == ["position fen"]
    assert session.game_session.reset_calls == ["reset fen"]


def test_view_render_frame_updates_viewport_and_renders_layers_in_order(monkeypatch: pytest.MonkeyPatch) -> None:
    """Render the configured frame boundaries and layers in the order expected by the runtime."""
    view, _, _, session = create_fake_view(monkeypatch)

    view.render_frame(width=300, height=400, x=10, y=20)

    assert session.geometry.updates == [Viewport(10, 20, 300, 400)]
    assert session.renderer.calls == [
        ("begin", Viewport(10, 20, 300, 400)),
        ("end", ()),
    ]
    assert session.render_order == ["board", "highlight", "piece", "annotation", "promotion"]


def test_view_render_frame_skips_layers_when_geometry_is_not_renderable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Still close the renderer frame when geometry reports that no layers should be drawn."""
    view, _, _, session = create_fake_view(monkeypatch)
    session.geometry.is_renderable = False

    view.render_frame()

    assert session.geometry.updates == [Viewport(1, 2, 100, 200)]
    assert session.renderer.calls == [
        ("begin", Viewport(1, 2, 100, 200)),
        ("end", ()),
    ]
    assert session.render_order == []
