# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Support API for pychessview.qt integration tests."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import pytest

SRC_DIR = str(Path(__file__).resolve().parents[2] / "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")
pytest.importorskip("chess")

from PySide6.QtCore import QEvent, QPointF, Qt  # noqa: E402
from PySide6.QtGui import QImage, QMouseEvent  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from pychessview import StandardChessFactory  # noqa: E402
from pychessview.engine.core.domain.game_spec import GameSpec  # noqa: E402
from pychessview.engine.core.primitives import Square  # noqa: E402
from pychessview.engine.interaction.input import MouseButton  # noqa: E402
from pychessview.engine.layout.primitives import Coord  # noqa: E402
from pychessview.qt.widget.chessboard_widget import ChessboardWidget  # noqa: E402


@dataclass(slots=True)
class ChessboardQtHarness:
    """Test harness for a real Qt widget backed by the real pychessview view.

    Attributes:
        widget: Widget under test.
        width: Widget width used for rendering and coordinate mapping.
        height: Widget height used for rendering and coordinate mapping.
    """

    widget: ChessboardWidget
    width: int
    height: int

    def paint_to_image(self) -> QImage:
        """Render the widget into an in-memory image.

        Returns:
            Image containing the widget's current rendered output.
        """
        image = QImage(self.width, self.height, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)
        self.widget.render(image)
        ensure_qapplication().processEvents()
        return image

    def coord_for_square(self, square: Square) -> Coord:
        """Return a stable widget coordinate inside the requested square.

        Args:
            square: Board square to locate in the current widget layout.

        Returns:
            A coordinate near the center of the rendered square.

        Raises:
            AssertionError: If the square is not present in the current widget layout.
        """
        self.paint_to_image()
        min_x: int | None = None
        max_x: int | None = None
        min_y: int | None = None
        max_y: int | None = None

        for y in range(0, self.height, 4):
            for x in range(0, self.width, 4):
                if self.widget.query.square_at(x, y) != square:
                    continue
                min_x = x if min_x is None else min(min_x, x)
                max_x = x if max_x is None else max(max_x, x)
                min_y = y if min_y is None else min(min_y, y)
                max_y = y if max_y is None else max(max_y, y)

        if min_x is None or max_x is None or min_y is None or max_y is None:
            raise AssertionError(f"square is not visible in the current widget layout: {square!r}")

        return Coord((min_x + max_x) // 2, (min_y + max_y) // 2)

    def coord_for_promotion_index(self, index: int) -> Coord:
        """Return a stable widget coordinate inside the requested promotion option.

        Args:
            index: Zero-based promotion option index to locate.

        Returns:
            A coordinate that resolves to the requested promotion option.

        Raises:
            AssertionError: If the promotion option is not visible.
        """
        self.paint_to_image()
        min_x: int | None = None
        max_x: int | None = None
        min_y: int | None = None
        max_y: int | None = None

        for y in range(0, self.height, 4):
            for x in range(0, self.width, 4):
                if self.widget.query.promotion_index_at(x, y) != index:
                    continue
                min_x = x if min_x is None else min(min_x, x)
                max_x = x if max_x is None else max(max_x, x)
                min_y = y if min_y is None else min(min_y, y)
                max_y = y if max_y is None else max(max_y, y)

        if min_x is None or max_x is None or min_y is None or max_y is None:
            raise AssertionError(f"promotion option is not visible in the current widget layout: {index}")

        return Coord((min_x + max_x) // 2, (min_y + max_y) // 2)


def ensure_qapplication() -> QApplication:
    """Return a QApplication instance for widget integration tests.

    Returns:
        Existing or newly created QApplication instance.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return cast(QApplication, app)


def create_standard_game_spec(default_fen: str | None = None) -> GameSpec:
    """Create the standard chess game specification used by Qt integration tests.

    Args:
        default_fen: Optional default FEN for the created game specification.

    Returns:
        Standard chess game specification.
    """
    return StandardChessFactory.create_game_spec(default_fen)


def create_standard_widget_harness(
    *,
    width: int = 640,
    height: int = 640,
    default_fen: str | None = None,
) -> ChessboardQtHarness:
    """Create a real Qt widget configured with the standard chess game.

    Args:
        width: Widget width used by the test harness.
        height: Widget height used by the test harness.
        default_fen: Optional default FEN for the standard chess widget.

    Returns:
        Harness around a real ``ChessboardWidget``.
    """
    ensure_qapplication()
    widget = ChessboardWidget(game_spec=create_standard_game_spec(default_fen))
    widget.resize(width, height)
    widget.show()
    ensure_qapplication().processEvents()
    harness = ChessboardQtHarness(widget=widget, width=width, height=height)
    harness.paint_to_image()
    return harness


def mouse_event(
    coord: Coord,
    *,
    event_type: QEvent.Type,
    button: Qt.MouseButton,
    buttons: Qt.MouseButton | None = None,
    modifiers: Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier,
) -> QMouseEvent:
    """Create a Qt mouse event for a widget coordinate.

    Args:
        coord: Widget coordinate to place in the event.
        event_type: Qt mouse event type.
        button: Button reported as the event trigger.
        buttons: Active button state for the event.
        modifiers: Keyboard modifiers active during the event.

    Returns:
        A ``QMouseEvent`` with consistent local, scene, and global coordinates.
    """
    point = QPointF(coord.x, coord.y)
    active_buttons = button if buttons is None else buttons
    return QMouseEvent(event_type, point, point, point, button, active_buttons, modifiers)


def send_press(harness: ChessboardQtHarness, square: Square) -> None:
    """Send a left-button widget press to a square.

    Args:
        harness: Harness whose widget should receive the event.
        square: Board square to press.
    """
    harness.widget.mousePressEvent(
        mouse_event(
            harness.coord_for_square(square),
            event_type=QEvent.Type.MouseButtonPress,
            button=Qt.MouseButton.LeftButton,
        )
    )


def send_move(harness: ChessboardQtHarness, square: Square) -> None:
    """Send a widget pointer move to a square.

    Args:
        harness: Harness whose widget should receive the event.
        square: Board square to move over.
    """
    harness.widget.mouseMoveEvent(
        mouse_event(
            harness.coord_for_square(square),
            event_type=QEvent.Type.MouseMove,
            button=Qt.MouseButton.NoButton,
            buttons=Qt.MouseButton.LeftButton,
        )
    )


def send_release(harness: ChessboardQtHarness, square: Square) -> None:
    """Send a left-button widget release to a square.

    Args:
        harness: Harness whose widget should receive the event.
        square: Board square to release over.
    """
    harness.widget.mouseReleaseEvent(
        mouse_event(
            harness.coord_for_square(square),
            event_type=QEvent.Type.MouseButtonRelease,
            button=Qt.MouseButton.LeftButton,
        )
    )


def drag_piece(harness: ChessboardQtHarness, from_square: Square, to_square: Square) -> None:
    """Drag a piece through widget mouse events.

    Args:
        harness: Harness whose widget should receive the interaction.
        from_square: Square containing the piece to move.
        to_square: Destination square.
    """
    send_press(harness, from_square)
    send_move(harness, to_square)
    send_release(harness, to_square)


def release_promotion_choice(harness: ChessboardQtHarness, index: int) -> None:
    """Release the mouse over a promotion choice.

    Args:
        harness: Harness whose widget should receive the release.
        index: Promotion choice index to select.
    """
    harness.widget.mouseReleaseEvent(
        mouse_event(
            harness.coord_for_promotion_index(index),
            event_type=QEvent.Type.MouseButtonRelease,
            button=Qt.MouseButton.LeftButton,
        )
    )


def image_has_visible_pixel(image: QImage) -> bool:
    """Return whether an image contains at least one non-transparent pixel.

    Args:
        image: Image to inspect after widget rendering.

    Returns:
        ``True`` when at least one pixel has a non-zero alpha channel.
    """
    for x in range(image.width()):
        for y in range(image.height()):
            if image.pixelColor(x, y).alpha() > 0:
                return True
    return False


def mouse_button_to_qt(button: MouseButton) -> Qt.MouseButton:
    """Return the Qt mouse button equivalent for a pychessview mouse button.

    Args:
        button: Chessboard mouse button to translate.

    Returns:
        Qt mouse button value used by widget-level integration tests.
    """
    if button is MouseButton.RIGHT:
        return Qt.MouseButton.RightButton
    return Qt.MouseButton.LeftButton
