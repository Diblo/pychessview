# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for the ChessboardWidget Qt facade."""

from collections.abc import Callable, Iterator
from typing import Any, cast

import pytest
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QPaintEvent
from PySide6.QtWidgets import QApplication, QWidget

from pychessview.engine.core.domain.game_spec import GameSpec
from pychessview.engine.core.primitives import PlayerColor
from pychessview.engine.interaction.controller_event_result import ControllerEventResult
from pychessview.qt.widget import chessboard_widget as widget_module
from pychessview.qt.widget.chessboard_widget import ChessboardWidget

from .._helpers import (
    PainterFake,
    RendererFake,
    WidgetControllerAdapterFake,
    WidgetViewFake,
    mouse_event,
    widget_controller_adapter,
    widget_renderer,
    widget_view,
)

pytestmark = [pytest.mark.unit, pytest.mark.requires_qt]


@pytest.fixture
def widget_factory(
    monkeypatch: pytest.MonkeyPatch,
    qapp: QApplication,
) -> Iterator[Callable[..., ChessboardWidget]]:
    """Create widgets with fake collaborators and clean them up after each test.

    Widget tests should exercise facade behavior without constructing the real
    core runtime or a real painter. The fixture replaces those collaborators
    with spies so tests can assert delegation contracts directly.
    """
    _ = qapp
    PainterFake.instances.clear()
    WidgetViewFake.instances.clear()
    WidgetControllerAdapterFake.instances.clear()
    created: list[ChessboardWidget] = []

    monkeypatch.setattr(widget_module, "QPainter", PainterFake)
    monkeypatch.setattr(widget_module, "QtRenderer", RendererFake)
    monkeypatch.setattr(widget_module, "View", WidgetViewFake)
    monkeypatch.setattr(widget_module, "QtControllerAdapter", WidgetControllerAdapterFake)

    def create(**kwargs: Any) -> ChessboardWidget:
        kwargs.setdefault("game_spec", cast(GameSpec, object()))
        widget = ChessboardWidget(**kwargs)
        created.append(widget)
        return widget

    yield create

    for widget in created:
        widget.deleteLater()


def test_chessboard_widget_constructs_underlying_view(widget_factory: Callable[..., ChessboardWidget]) -> None:
    """Create the core view and controller adapter without changing constructor options.

    The Qt widget is only a facade over the backend-agnostic view. Constructor
    values such as the game specification, player color, and default FEN must
    reach the view unchanged so Qt setup does not alter board initialization.
    """
    game_spec = cast(GameSpec, object())
    widget = widget_factory(game_spec=game_spec, player=PlayerColor.BLACK, default_fen="fen")
    view = widget_view(widget)

    assert isinstance(widget_renderer(widget), RendererFake)
    assert view.constructor_args["game_spec"] is game_spec
    assert view.constructor_args["player"] is PlayerColor.BLACK
    assert view.constructor_args["default_fen"] == "fen"
    assert widget_controller_adapter(widget).view is view
    assert widget.sizeHint().width() == 512
    assert widget.minimumSizeHint().width() == 30


def test_chessboard_widget_delegates_view_properties(widget_factory: Callable[..., ChessboardWidget]) -> None:
    """Expose view-owned runtime properties without copying or wrapping them.

    Consumers use the widget as the Qt entry point to the core view. Returning
    the same objects preserves identity-sensitive state such as theme, sessions,
    settings, and query helpers.
    """
    widget = widget_factory()
    view = widget_view(widget)

    assert widget.theme is view.theme
    assert widget.settings is view.settings
    assert widget.fen == "initial-fen"
    assert widget.game is view.game
    assert widget.interaction is view.interaction
    assert widget.annotation is view.annotation
    assert widget.query is view.query


def test_controller_enabled_forwards_to_underlying_view(widget_factory: Callable[..., ChessboardWidget]) -> None:
    """Forward controller enablement to the underlying view instead of shadowing it.

    Input enablement is owned by the core view. The widget must not keep a
    separate flag because that would allow facade state and runtime state to
    drift apart after toggling interaction.
    """
    widget = widget_factory()
    view = widget_view(widget)

    assert widget.controller_enabled is True

    widget.controller_enabled = False

    assert view.controller_enabled is False
    assert widget.controller_enabled is False


def test_chessboard_widget_delegates_view_mutation_methods(widget_factory: Callable[..., ChessboardWidget]) -> None:
    """Forward game and position mutations to the core view with arguments intact.

    The Qt layer must not interpret game specifications, FEN strings, or
    promotion options. Preserving the exact arguments keeps board-state
    semantics inside the backend-agnostic view.
    """
    widget = widget_factory()
    view = widget_view(widget)
    next_game_spec = cast(GameSpec, object())

    widget.load_game(
        next_game_spec,
        player=PlayerColor.BLACK,
        default_fen="next-fen",
        white_promotion_pieces=(),
        black_promotion_pieces=(),
    )
    widget.load_position_from_fen("loaded-fen")
    widget.reset_board("reset-fen")

    assert view.load_game_calls == [
        {
            "game_spec": next_game_spec,
            "player": PlayerColor.BLACK,
            "default_fen": "next-fen",
            "white_promotion_pieces": (),
            "black_promotion_pieces": (),
        }
    ]
    assert view.loaded_fens == ["loaded-fen"]
    assert view.reset_calls == ["reset-fen"]


def test_theme_setter_updates_underlying_view(widget_factory: Callable[..., ChessboardWidget]) -> None:
    """Assign themes through the widget without creating a second theme owner.

    Rendering uses the view-owned theme, so setting ``widget.theme`` must update
    that same object reference rather than storing a facade-only value.
    """
    widget = widget_factory()
    view = widget_view(widget)
    new_theme = cast(Any, object())

    widget.theme = new_theme

    assert view.theme is new_theme
    assert widget.theme is new_theme


def test_paint_event_sets_renderer_painter_and_renders_frame(widget_factory: Callable[..., ChessboardWidget]) -> None:
    """Render a frame with a widget-owned painter and close that painter afterwards.

    The renderer needs the active painter for the current paint event, but the
    widget owns painter lifetime. This protects against missed frame rendering
    and leaked Qt painter state.
    """
    widget = widget_factory()
    widget.resize(321, 123)
    view = widget_view(widget)
    renderer = widget_renderer(widget)

    widget.paintEvent(cast(QPaintEvent, object()))

    assert len(PainterFake.instances) == 1
    assert PainterFake.instances[0].target is widget
    assert renderer.painters == [PainterFake.instances[0]]
    assert view.render_frame_calls == [(321, 123)]
    assert PainterFake.instances[0].ended is True


@pytest.mark.parametrize(
    ("adapter_result", "expected_calls"),
    [
        (ControllerEventResult(handled=True, requires_render=True), ["update", "grab"]),
        (ControllerEventResult(), ["super"]),
    ],
)
def test_mouse_press_event_uses_adapter_result_to_choose_widget_behavior(
    monkeypatch: pytest.MonkeyPatch,
    widget_factory: Callable[..., ChessboardWidget],
    adapter_result: ControllerEventResult,
    expected_calls: list[str],
) -> None:
    """Consume handled press events and leave unhandled presses to QWidget.

    ControllerEventResult is the boundary between interaction policy and Qt
    event policy. Handled presses should repaint and grab the mouse for drag
    continuity, while unhandled presses must keep normal QWidget behavior.
    """
    widget = widget_factory()
    adapter = widget_controller_adapter(widget)
    adapter.press_result = adapter_result
    calls: list[str] = []

    monkeypatch.setattr(ChessboardWidget, "update", lambda self: calls.append("update"))  # type: ignore
    monkeypatch.setattr(ChessboardWidget, "grabMouse", lambda self: calls.append("grab"))  # type: ignore
    monkeypatch.setattr(QWidget, "mousePressEvent", lambda self, event: calls.append("super"))  # type: ignore

    event = mouse_event(event_type=QEvent.Type.MouseButtonPress, button=Qt.MouseButton.LeftButton)
    widget.mousePressEvent(event)

    assert adapter.calls == [("press", event)]
    assert calls == expected_calls


@pytest.mark.parametrize(
    ("adapter_result", "expected_calls"),
    [
        (ControllerEventResult(handled=True, requires_render=True), ["update"]),
        (ControllerEventResult(), ["super"]),
    ],
)
def test_mouse_move_event_uses_adapter_result_to_choose_widget_behavior(
    monkeypatch: pytest.MonkeyPatch,
    widget_factory: Callable[..., ChessboardWidget],
    adapter_result: ControllerEventResult,
    expected_calls: list[str],
) -> None:
    """Use the adapter result as the sole policy for move repaint and fallback.

    Pointer movement should not trigger widget updates unless the controller
    consumed the event and requested rendering. Unhandled movement remains
    available to the base Qt widget implementation.
    """
    widget = widget_factory()
    adapter = widget_controller_adapter(widget)
    adapter.move_result = adapter_result
    calls: list[str] = []

    monkeypatch.setattr(ChessboardWidget, "update", lambda self: calls.append("update"))  # type: ignore
    monkeypatch.setattr(QWidget, "mouseMoveEvent", lambda self, event: calls.append("super"))  # type: ignore

    event = mouse_event(event_type=QEvent.Type.MouseMove, button=Qt.MouseButton.LeftButton)
    widget.mouseMoveEvent(event)

    assert adapter.calls == [("move", event)]
    assert calls == expected_calls


@pytest.mark.parametrize(
    ("adapter_result", "expected_calls"),
    [
        (ControllerEventResult(handled=True, requires_render=True), ["update", "release"]),
        (ControllerEventResult(), ["super", "release"]),
    ],
)
def test_mouse_release_event_uses_adapter_result_and_always_releases_mouse(
    monkeypatch: pytest.MonkeyPatch,
    widget_factory: Callable[..., ChessboardWidget],
    adapter_result: ControllerEventResult,
    expected_calls: list[str],
) -> None:
    """Always release the mouse grab after release handling finishes.

    The widget may either consume the release itself or delegate to ``QWidget``,
    but a stale mouse grab would break later input. The cleanup contract must
    hold for both handled and unhandled release events.
    """
    widget = widget_factory()
    adapter = widget_controller_adapter(widget)
    adapter.release_result = adapter_result
    calls: list[str] = []

    monkeypatch.setattr(ChessboardWidget, "update", lambda self: calls.append("update"))  # type: ignore
    monkeypatch.setattr(ChessboardWidget, "releaseMouse", lambda self: calls.append("release"))  # type: ignore
    monkeypatch.setattr(QWidget, "mouseReleaseEvent", lambda self, event: calls.append("super"))  # type: ignore

    event = mouse_event(event_type=QEvent.Type.MouseButtonRelease, button=Qt.MouseButton.LeftButton)
    widget.mouseReleaseEvent(event)

    assert adapter.calls == [("release", event)]
    assert calls == expected_calls
