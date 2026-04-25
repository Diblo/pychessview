# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for Qt mouse event helper functions."""

import pytest
from PySide6.QtCore import Qt

from pychessview.engine.interaction.input.modifiers import Modifier
from pychessview.engine.layout.primitives import Coord
from pychessview.qt.widget.events import event_coord, event_modifier

from .._helpers import mouse_event

pytestmark = [pytest.mark.unit, pytest.mark.requires_qt]


@pytest.mark.parametrize(
    ("x", "y", "expected"),
    [
        (12.9, 18.1, Coord(12, 18)),
        (0.0, 0.0, Coord(0, 0)),
        (-1.9, -3.1, Coord(-1, -3)),
    ],
)
def test_event_coord_truncates_qt_position_to_integer_coord(x: float, y: float, expected: Coord) -> None:
    """Convert Qt floating-point positions into board coordinates by truncation.

    The event helper is the seam between Qt floating-point positions and the
    board's integer coordinate system. Positive and negative values must follow
    Python ``int`` semantics so adapter routing receives predictable board
    coordinates.
    """
    assert event_coord(mouse_event(x, y)) == expected


@pytest.mark.parametrize(
    ("qt_modifier", "expected_modifier"),
    [
        (Qt.KeyboardModifier.ShiftModifier, Modifier.SHIFT),
        (Qt.KeyboardModifier.ControlModifier, Modifier.CTRL),
        (Qt.KeyboardModifier.AltModifier, Modifier.ALT),
        (Qt.KeyboardModifier.MetaModifier, None),
        (Qt.KeyboardModifier.ShiftModifier | Qt.KeyboardModifier.ControlModifier, None),
        (
            Qt.KeyboardModifier.ShiftModifier | Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier,
            None,
        ),
        (Qt.KeyboardModifier.NoModifier, None),
    ],
)
def test_event_modifier_returns_only_single_supported_modifier(
    qt_modifier: Qt.KeyboardModifier,
    expected_modifier: Modifier | None,
) -> None:
    """Return a modifier only when exactly one supported keyboard modifier is active.

    Shift, Control, and Alt map to controller modifiers. Unsupported modifiers,
    no modifier, and simultaneous supported modifiers all produce ``None`` so
    annotation input does not receive ambiguous modifier intent.
    """
    assert event_modifier(mouse_event(1.0, 2.0, modifiers=qt_modifier)) is expected_modifier
