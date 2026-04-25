# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for QtControllerAdapter event translation and routing."""

import pytest
from PySide6.QtCore import QEvent, Qt

from pychessview.engine.interaction.controller_event_result import ControllerEventResult
from pychessview.engine.interaction.input.modifiers import Modifier
from pychessview.engine.interaction.input.mouse_buttons import MouseButton

from .._helpers import ControllerAdapterViewFake, controller_adapter_for, mouse_event

pytestmark = [pytest.mark.unit, pytest.mark.requires_qt]


@pytest.mark.parametrize(
    ("event_type", "button", "expected_call"),
    [
        (QEvent.Type.MouseButtonPress, Qt.MouseButton.LeftButton, ("press", (10, 11, None, MouseButton.LEFT))),
        (QEvent.Type.MouseButtonPress, Qt.MouseButton.RightButton, ("press", (10, 11, None, MouseButton.RIGHT))),
        (QEvent.Type.MouseButtonRelease, Qt.MouseButton.LeftButton, ("release", (10, 11, None, MouseButton.LEFT))),
        (QEvent.Type.MouseButtonRelease, Qt.MouseButton.RightButton, ("release", (10, 11, None, MouseButton.RIGHT))),
    ],
)
def test_adapter_forwards_supported_press_and_release_buttons(
    event_type: QEvent.Type,
    button: Qt.MouseButton,
    expected_call: tuple[str, tuple[int, int, None, MouseButton]],
) -> None:
    """Normalize supported press and release buttons before controller dispatch.

    Qt-specific button values must become controller-level ``MouseButton``
    values before reaching board interaction. Coordinates are also truncated at
    the adapter boundary so the controller receives only core-domain input.
    """
    view = ControllerAdapterViewFake()
    adapter = controller_adapter_for(view)
    event = mouse_event(10.9, 11.1, event_type=event_type, button=button)

    if event_type == QEvent.Type.MouseButtonPress:
        result = adapter.handle_press(event)
    else:
        result = adapter.handle_release(event)

    assert result == ControllerEventResult(handled=True)
    assert view.query.calls == [(10, 11)]
    assert view.controller.calls == [expected_call]


def test_handle_move_routes_inside_view_to_controller() -> None:
    """Route inside-board pointer movement without inventing button state.

    Move events should forward translated coordinates and modifiers only. This
    keeps drag updates independent of press/release button translation.
    """
    view = ControllerAdapterViewFake()
    adapter = controller_adapter_for(view)
    event = mouse_event(12.9, 18.1, event_type=QEvent.Type.MouseMove)

    result = adapter.handle_move(event)

    assert result == ControllerEventResult(handled=True)
    assert view.query.calls == [(12, 18)]
    assert view.controller.calls == [("move", (12, 18, None))]


@pytest.mark.parametrize(
    ("event_type", "button", "expected_call", "expected_result"),
    [
        (
            QEvent.Type.MouseButtonPress,
            Qt.MouseButton.LeftButton,
            ("press_outside", None),
            ControllerEventResult(handled=True),
        ),
        (
            QEvent.Type.MouseMove,
            Qt.MouseButton.NoButton,
            ("move_outside", None),
            ControllerEventResult(requires_render=True),
        ),
        (
            QEvent.Type.MouseButtonRelease,
            Qt.MouseButton.LeftButton,
            ("release_outside", None),
            ControllerEventResult(handled=True, requires_render=True),
        ),
    ],
)
def test_adapter_routes_outside_view_events_to_matching_cleanup_handler(
    event_type: QEvent.Type,
    button: Qt.MouseButton,
    expected_call: tuple[str, None],
    expected_result: ControllerEventResult,
) -> None:
    """Dispatch outside-board events to cleanup handlers and propagate their result.

    Coordinates outside the board should not enter normal press, move, or
    release handlers. The exact outside-handler result must return to the widget
    so repaint and event-consumption policy stays controller-owned.
    """
    view = ControllerAdapterViewFake(inside=False)
    view.controller.press_outside_result = ControllerEventResult(handled=True)
    view.controller.move_outside_result = ControllerEventResult(requires_render=True)
    view.controller.release_outside_result = ControllerEventResult(handled=True, requires_render=True)
    adapter = controller_adapter_for(view)
    event = mouse_event(1.9, 2.1, event_type=event_type, button=button)

    if event_type == QEvent.Type.MouseButtonPress:
        result = adapter.handle_press(event)
    elif event_type == QEvent.Type.MouseButtonRelease:
        result = adapter.handle_release(event)
    else:
        result = adapter.handle_move(event)

    assert result == expected_result
    assert view.query.calls == [(1, 2)]
    assert view.controller.calls == [expected_call]


@pytest.mark.parametrize(
    ("event_type", "method_name"),
    [
        (QEvent.Type.MouseButtonPress, "handle_press"),
        (QEvent.Type.MouseButtonRelease, "handle_release"),
    ],
)
def test_adapter_ignores_unsupported_press_and_release_buttons(
    event_type: QEvent.Type,
    method_name: str,
) -> None:
    """Reject unsupported mouse buttons before board lookup or controller dispatch.

    Middle-button input has no controller-level mapping. Returning a neutral
    result without querying board bounds prevents unsupported Qt input from
    accidentally entering the interaction layer.
    """
    view = ControllerAdapterViewFake()
    adapter = controller_adapter_for(view)
    event = mouse_event(10.9, 11.1, event_type=event_type, button=Qt.MouseButton.MiddleButton)

    result = getattr(adapter, method_name)(event)

    assert result == ControllerEventResult()
    assert view.query.calls == []
    assert view.controller.calls == []


@pytest.mark.parametrize(
    ("event_type", "qt_modifier", "expected_call"),
    [
        (
            QEvent.Type.MouseButtonPress,
            Qt.KeyboardModifier.ShiftModifier,
            ("press", (20, 21, Modifier.SHIFT, MouseButton.LEFT)),
        ),
        (QEvent.Type.MouseMove, Qt.KeyboardModifier.ControlModifier, ("move", (22, 23, Modifier.CTRL))),
        (
            QEvent.Type.MouseButtonRelease,
            Qt.KeyboardModifier.AltModifier,
            ("release", (24, 25, Modifier.ALT, MouseButton.LEFT)),
        ),
    ],
)
def test_adapter_forwards_single_event_modifier_translation(
    event_type: QEvent.Type,
    qt_modifier: Qt.KeyboardModifier,
    expected_call: tuple[str, tuple[int, int, Modifier, MouseButton]],
) -> None:
    """Forward exactly one supported modifier across press, move, and release events.

    Modifier mapping belongs to the shared event helper. The adapter contract is
    to pass that translated value through unchanged while still routing each Qt
    event type to the correct controller method.
    """
    view = ControllerAdapterViewFake()
    adapter = controller_adapter_for(view)
    event = mouse_event(
        expected_call[1][0] + 0.9,
        expected_call[1][1] + 0.1,
        event_type=event_type,
        button=Qt.MouseButton.LeftButton,
        modifiers=qt_modifier,
    )

    if event_type == QEvent.Type.MouseButtonPress:
        result = adapter.handle_press(event)
    elif event_type == QEvent.Type.MouseButtonRelease:
        result = adapter.handle_release(event)
    else:
        result = adapter.handle_move(event)

    assert result == ControllerEventResult(handled=True)
    assert view.controller.calls == [expected_call]


def test_adapter_forwards_none_for_combined_modifiers() -> None:
    """Forward ``None`` for ambiguous multi-modifier input.

    The real ``event_modifier`` implementation only returns a modifier when
    exactly one supported modifier is active; combined Shift+Ctrl input is
    intentionally forwarded as ``None``.
    """
    view = ControllerAdapterViewFake()
    adapter = controller_adapter_for(view)
    event = mouse_event(
        26.9,
        27.1,
        event_type=QEvent.Type.MouseMove,
        modifiers=Qt.KeyboardModifier.ShiftModifier | Qt.KeyboardModifier.ControlModifier,
    )

    result = adapter.handle_move(event)

    assert result == ControllerEventResult(handled=True)
    assert view.controller.calls == [("move", (26, 27, None))]
