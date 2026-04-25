# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for controller proxy delegation."""

from __future__ import annotations

import pytest

from pychessview.engine.interaction.controller_proxy import ControllerProxy
from pychessview.engine.interaction.input.modifiers import Modifier
from pychessview.engine.interaction.input.mouse_buttons import MouseButton
from pychessview.engine.layout.primitives import Coord

from .._helpers import ControllerProxySpy

pytestmark = pytest.mark.unit


def test_controller_proxy_forwards_all_event_methods_to_active_controller() -> None:
    """Delegate every pointer event to the active implementation without changing arguments or results."""
    controller = ControllerProxySpy("initial")
    proxy = ControllerProxy(controller)
    coord = Coord(12, 34)

    assert proxy.on_press(coord, MouseButton.RIGHT, Modifier.SHIFT) is controller.press_result
    assert proxy.on_press_outside_view() is controller.outside_press_result
    assert proxy.on_pointer_move(coord, Modifier.CTRL) is controller.move_result
    assert proxy.on_pointer_move_outside_view() is controller.outside_move_result
    assert proxy.on_release(coord, MouseButton.LEFT, Modifier.ALT) is controller.release_result
    assert proxy.on_release_outside_view() is controller.outside_release_result
    assert controller.calls == [
        ("press", (coord, MouseButton.RIGHT, Modifier.SHIFT)),
        ("press_outside", ()),
        ("move", (coord, Modifier.CTRL)),
        ("move_outside", ()),
        ("release", (coord, MouseButton.LEFT, Modifier.ALT)),
        ("release_outside", ()),
    ]


def test_controller_proxy_switches_delegation_target_for_future_events() -> None:
    """Route future events to the replacement controller without keeping stale delegation state."""
    first = ControllerProxySpy("first")
    second = ControllerProxySpy("second")
    proxy = ControllerProxy(first)
    coord = Coord(3, 4)

    proxy.switch_controller(second)
    result = proxy.on_press(coord, MouseButton.LEFT)

    assert result is second.press_result
    assert first.calls == []
    assert second.calls == [("press", (coord, MouseButton.LEFT, None))]
