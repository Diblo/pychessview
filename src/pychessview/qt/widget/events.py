# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Qt event helpers for the pychessview.qt package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt

from pychessview.engine.interaction.input.modifiers import Modifier
from pychessview.engine.layout.primitives import Coord

if TYPE_CHECKING:
    from PySide6.QtGui import QMouseEvent


def event_coord(event: QMouseEvent) -> Coord:
    """Return the mouse event position converted to board coordinates.

    Args:
        event: Mouse event whose position should be translated.

    Returns:
        Mouse position converted to board coordinates.
    """
    position = event.position()
    return Coord(int(position.x()), int(position.y()))


def event_modifier(event: QMouseEvent) -> Modifier | None:
    """Return the active single-key modifier for the mouse event.

    Args:
        event: Mouse event whose keyboard modifiers should be translated.

    Returns:
        Active single-key modifier for the event, if any.
    """
    modifiers = event.modifiers()
    active: list[Modifier] = []
    if modifiers & Qt.KeyboardModifier.ShiftModifier:
        active.append(Modifier.SHIFT)
    if modifiers & Qt.KeyboardModifier.ControlModifier:
        active.append(Modifier.CTRL)
    if modifiers & Qt.KeyboardModifier.AltModifier:
        active.append(Modifier.ALT)
    if len(active) != 1:
        return None
    return active[0]
