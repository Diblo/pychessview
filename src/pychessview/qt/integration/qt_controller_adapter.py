# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Qt event adapter for pychessview controllers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt

from pychessview.engine.interaction.controller_event_result import ControllerEventResult
from pychessview.engine.interaction.input.mouse_buttons import MouseButton

from ..widget.events import event_coord, event_modifier

if TYPE_CHECKING:
    from PySide6.QtGui import QMouseEvent

    from pychessview.engine.view import View


class QtControllerAdapter:
    """Adapt Qt mouse events to the pychessview controller API."""

    __slots__ = ("_view",)

    _view: View

    def __init__(self, view: View) -> None:
        """Initialize the Qt controller adapter with the controller used to process widget events.

        Args:
            view: Value used to initialize ``view``.
        """
        self._view = view

    def handle_press(self, event: QMouseEvent) -> ControllerEventResult:
        """Handle a Qt mouse press event.

        Args:
            event: Qt event to handle.

        Returns:
            ControllerEventResult describing the outcome of the controller interaction.
        """
        button = _mouse_button(event)
        if button is None:
            return ControllerEventResult()

        coord = event_coord(event)
        if not self._view.query.is_inside(coord.x, coord.y):
            return self._view.controller.on_press_outside_view()
        return self._view.controller.on_press(coord, button, event_modifier(event))

    def handle_move(self, event: QMouseEvent) -> ControllerEventResult:
        """Handle a Qt mouse move event.

        Args:
            event: Qt event to handle.

        Returns:
            ControllerEventResult describing the outcome of the controller interaction.
        """
        coord = event_coord(event)
        if not self._view.query.is_inside(coord.x, coord.y):
            return self._view.controller.on_pointer_move_outside_view()
        return self._view.controller.on_pointer_move(coord, event_modifier(event))

    def handle_release(self, event: QMouseEvent) -> ControllerEventResult:
        """Handle a Qt mouse release event.

        Args:
            event: Qt event to handle.

        Returns:
            ControllerEventResult describing the outcome of the controller interaction.
        """
        button = _mouse_button(event)
        if button is None:
            return ControllerEventResult()

        coord = event_coord(event)
        if not self._view.query.is_inside(coord.x, coord.y):
            return self._view.controller.on_release_outside_view()
        return self._view.controller.on_release(coord, button, event_modifier(event))


def _mouse_button(event: QMouseEvent) -> MouseButton | None:
    """Return the pychessview mouse-button enum for a Qt mouse event.

    Args:
        event: Qt mouse event to inspect.

    Returns:
        Matching pychessview mouse button, or ``None`` when the button is not supported.
    """
    if event.button() == Qt.MouseButton.LeftButton:
        return MouseButton.LEFT
    if event.button() == Qt.MouseButton.RightButton:
        return MouseButton.RIGHT
    return None
