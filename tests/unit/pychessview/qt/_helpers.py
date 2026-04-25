# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Shared helpers for pychessview.qt unit tests."""

from pathlib import Path
from types import SimpleNamespace
from typing import ClassVar, cast

from PySide6.QtCore import QEvent, QPointF, QRectF, Qt
from PySide6.QtGui import QImage, QMouseEvent

from pychessview import View
from pychessview.engine.core.primitives import PlayerColor
from pychessview.engine.interaction.controller_event_result import ControllerEventResult
from pychessview.engine.interaction.input.modifiers import Modifier
from pychessview.engine.interaction.input.mouse_buttons import MouseButton
from pychessview.engine.layout.primitives import Coord
from pychessview.qt.integration.qt_controller_adapter import QtControllerAdapter
from pychessview.qt.renderer.qt_renderer import QtRenderer


def mouse_event(
    x: float = 12.0,
    y: float = 18.0,
    *,
    event_type: QEvent.Type = QEvent.Type.MouseMove,
    button: Qt.MouseButton = Qt.MouseButton.NoButton,
    modifiers: Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier,
) -> QMouseEvent:
    """Create a Qt mouse event with consistent local, scene, and global coordinates.

    Args:
        x: Horizontal pointer coordinate used for all Qt event positions.
        y: Vertical pointer coordinate used for all Qt event positions.
        event_type: Qt mouse event type to create.
        button: Qt mouse button reported by the event.
        modifiers: Qt keyboard modifiers active for the event.

    Returns:
        A ``QMouseEvent`` configured for unit tests that exercise Qt event adapters.
    """
    point = QPointF(x, y)
    return QMouseEvent(event_type, point, point, point, button, button, modifiers)


def image_has_visible_pixel(image: QImage) -> bool:
    """Return whether an image contains at least one non-transparent pixel.

    Args:
        image: Image to inspect after a drawing operation.

    Returns:
        ``True`` when at least one pixel has a non-zero alpha channel.
    """
    for x in range(image.width()):
        for y in range(image.height()):
            if image.pixelColor(x, y).alpha() > 0:
                return True
    return False


class ControllerAdapterQueryFake:
    """Query fake that records inside-view checks performed by the adapter.

    Attributes:
        inside: Result returned from ``is_inside`` for every queried coordinate.
        calls: Coordinates passed to ``is_inside`` in call order.
    """

    def __init__(self, *, inside: bool = True) -> None:
        self.inside = inside
        self.calls: list[tuple[int, int]] = []

    def is_inside(self, x: int, y: int) -> bool:
        self.calls.append((x, y))
        return self.inside


class ControllerFake:
    """Controller fake that records routed Qt adapter calls and return values.

    Attributes:
        calls: Controller method calls recorded as method names and normalized arguments.
        press_result: Result returned from inside-view press handling.
        move_result: Result returned from inside-view move handling.
        release_result: Result returned from inside-view release handling.
        press_outside_result: Result returned from outside-view press cleanup.
        move_outside_result: Result returned from outside-view move cleanup.
        release_outside_result: Result returned from outside-view release cleanup.
    """

    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []
        self.press_result = ControllerEventResult(handled=True)
        self.move_result = ControllerEventResult(handled=True)
        self.release_result = ControllerEventResult(handled=True)
        self.press_outside_result = ControllerEventResult()
        self.move_outside_result = ControllerEventResult()
        self.release_outside_result = ControllerEventResult()

    def on_press(self, coord: Coord, button: MouseButton, modifier: Modifier | None = None) -> ControllerEventResult:
        self.calls.append(("press", (coord.x, coord.y, modifier, button)))
        return self.press_result

    def on_press_outside_view(self) -> ControllerEventResult:
        self.calls.append(("press_outside", None))
        return self.press_outside_result

    def on_pointer_move(self, coord: Coord, modifier: Modifier | None = None) -> ControllerEventResult:
        self.calls.append(("move", (coord.x, coord.y, modifier)))
        return self.move_result

    def on_pointer_move_outside_view(self) -> ControllerEventResult:
        self.calls.append(("move_outside", None))
        return self.move_outside_result

    def on_release(self, coord: Coord, button: MouseButton, modifier: Modifier | None = None) -> ControllerEventResult:
        self.calls.append(("release", (coord.x, coord.y, modifier, button)))
        return self.release_result

    def on_release_outside_view(self) -> ControllerEventResult:
        self.calls.append(("release_outside", None))
        return self.release_outside_result


class ControllerAdapterViewFake:
    """Minimal view fake exposing the attributes used by ``QtControllerAdapter``.

    Attributes:
        query: Fake board query object used for inside/outside routing decisions.
        controller: Fake controller object that records routed adapter calls.
    """

    def __init__(self, *, inside: bool = True) -> None:
        self.query = ControllerAdapterQueryFake(inside=inside)
        self.controller = ControllerFake()


def controller_adapter_for(view: ControllerAdapterViewFake) -> QtControllerAdapter:
    """Create the real Qt controller adapter around the adapter test fake view.

    Args:
        view: Fake view that exposes the query and controller attributes used by
            ``QtControllerAdapter``.

    Returns:
        A ``QtControllerAdapter`` configured for unit tests.
    """
    return QtControllerAdapter(cast(View, view))


class PainterFake:
    """Fake painter used to observe widget paint orchestration without real drawing.

    Attributes:
        instances: Painters created by widget paint events in construction order.
        target: Object the painter was constructed for.
        ended: Whether ``end`` has been called.
    """

    instances: ClassVar[list["PainterFake"]] = []

    def __init__(self, target: object) -> None:
        self.target = target
        self.ended = False
        self.instances.append(self)

    def end(self) -> None:
        self.ended = True


class RendererFake:
    """Renderer fake that records which painter the widget installs for a frame.

    Attributes:
        painters: Painter objects passed to ``set_painter`` in call order.
    """

    def __init__(self) -> None:
        self.painters: list[object] = []

    def set_painter(self, painter: object) -> None:
        self.painters.append(painter)


class SpyRenderer(QtRenderer):
    """Spy renderer that records whether raster or SVG rendering paths are used.

    Attributes:
        svg_calls: SVG image paths and target rectangles routed through the SVG branch.
        raster_calls: Raster image paths and target rectangles routed through the raster branch.
    """

    __slots__ = "svg_calls", "raster_calls"

    svg_calls: list[tuple[Path, tuple[float, float, float, float]]]
    raster_calls: list[tuple[Path, tuple[float, float, float, float]]]

    def __init__(self) -> None:
        super().__init__()
        self.svg_calls = []
        self.raster_calls = []

    def _draw_svg(self, image_path: Path, rect: QRectF) -> None:
        self.svg_calls.append((image_path, (rect.x(), rect.y(), rect.width(), rect.height())))

    def _draw_raster(self, image_path: Path, rect: QRectF) -> None:
        self.raster_calls.append((image_path, (rect.x(), rect.y(), rect.width(), rect.height())))


class WidgetViewFake:
    """Minimal fake ``View`` implementation used to unit-test the Qt widget facade.

    Attributes:
        instances: Fake views created by widget construction in call order.
        constructor_args: Constructor values forwarded by the widget.
        load_game_calls: Arguments forwarded to ``load_game``.
        loaded_fens: FEN strings forwarded to ``load_position_from_fen``.
        reset_calls: FEN strings forwarded to ``reset_board``.
        render_frame_calls: Viewport sizes forwarded to ``render_frame``.
    """

    instances: ClassVar[list["WidgetViewFake"]] = []

    def __init__(
        self,
        renderer: object,
        game_spec: object,
        *,
        player: PlayerColor = PlayerColor.WHITE,
        default_fen: str | None = None,
        white_promotion_pieces: tuple[object, ...] | None = None,
        black_promotion_pieces: tuple[object, ...] | None = None,
        game_session_class: type[object] | None = None,
        interaction_session_class: type[object] | None = None,
        annotation_session_class: type[object] | None = None,
        promotion_session_class: type[object] | None = None,
    ) -> None:
        self.renderer = renderer
        self.constructor_args = {
            "game_spec": game_spec,
            "player": player,
            "default_fen": default_fen,
            "white_promotion_pieces": white_promotion_pieces,
            "black_promotion_pieces": black_promotion_pieces,
            "game_session_class": game_session_class,
            "interaction_session_class": interaction_session_class,
            "annotation_session_class": annotation_session_class,
            "promotion_session_class": promotion_session_class,
        }
        self.theme = object()
        self.settings = SimpleNamespace(player=player)
        self.fen = default_fen or "initial-fen"
        self.game = object()
        self.interaction = object()
        self.annotation = object()
        self.query = object()
        self.controller_enabled = True
        self.load_game_calls: list[dict[str, object]] = []
        self.loaded_fens: list[str] = []
        self.reset_calls: list[str | None] = []
        self.render_frame_calls: list[tuple[int, int]] = []
        self.instances.append(self)

    def load_game(
        self,
        game_spec: object,
        *,
        player: PlayerColor = PlayerColor.WHITE,
        default_fen: str | None = None,
        white_promotion_pieces: tuple[object, ...] | None = None,
        black_promotion_pieces: tuple[object, ...] | None = None,
    ) -> None:
        self.load_game_calls.append(
            {
                "game_spec": game_spec,
                "player": player,
                "default_fen": default_fen,
                "white_promotion_pieces": white_promotion_pieces,
                "black_promotion_pieces": black_promotion_pieces,
            }
        )

    def load_position_from_fen(self, fen: str) -> None:
        self.loaded_fens.append(fen)
        self.fen = fen

    def reset_board(self, fen: str | None = None) -> None:
        self.reset_calls.append(fen)

    def render_frame(self, width: int, height: int) -> None:
        self.render_frame_calls.append((width, height))


class WidgetControllerAdapterFake:
    """Qt controller adapter fake used to unit-test widget event forwarding.

    Attributes:
        instances: Fake adapters created by widget construction in call order.
        view: Fake view passed into the adapter by the widget.
        press_result: Result returned from ``handle_press``.
        move_result: Result returned from ``handle_move``.
        release_result: Result returned from ``handle_release``.
        calls: Events forwarded by the widget to the adapter.
    """

    instances: ClassVar[list["WidgetControllerAdapterFake"]] = []

    def __init__(self, view: WidgetViewFake) -> None:
        self.view = view
        self.press_result = ControllerEventResult()
        self.move_result = ControllerEventResult()
        self.release_result = ControllerEventResult()
        self.calls: list[tuple[str, QMouseEvent]] = []
        self.instances.append(self)

    def handle_press(self, event: QMouseEvent) -> ControllerEventResult:
        self.calls.append(("press", event))
        return self.press_result

    def handle_move(self, event: QMouseEvent) -> ControllerEventResult:
        self.calls.append(("move", event))
        return self.move_result

    def handle_release(self, event: QMouseEvent) -> ControllerEventResult:
        self.calls.append(("release", event))
        return self.release_result


def widget_view(widget: object) -> WidgetViewFake:
    """Return the most recently created fake widget view.

    Args:
        widget: Widget instance whose construction caused the fake view to be created.

    Returns:
        The latest ``WidgetViewFake`` recorded by the fake constructor.
    """
    _ = widget
    return WidgetViewFake.instances[-1]


def widget_renderer(widget: object) -> RendererFake:
    """Return the fake renderer attached to the widget's fake view.

    Args:
        widget: Widget whose fake renderer should be inspected.

    Returns:
        The ``RendererFake`` used by the widget under test.
    """
    return cast(RendererFake, widget_view(widget).renderer)


def widget_controller_adapter(widget: object) -> WidgetControllerAdapterFake:
    """Return the most recently created fake widget controller adapter.

    Args:
        widget: Widget instance whose construction caused the fake adapter to be created.

    Returns:
        The latest ``WidgetControllerAdapterFake`` recorded by the fake constructor.
    """
    _ = widget
    return WidgetControllerAdapterFake.instances[-1]
