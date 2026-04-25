# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for the standard chess controller."""

import pytest

from pychessview.engine.core.annotation_types import CircleType
from pychessview.engine.interaction.controller_event_result import ControllerEventResult
from pychessview.engine.interaction.input.modifiers import Modifier
from pychessview.engine.interaction.input.mouse_buttons import MouseButton

from ..._helpers import (
    STANDARD_CONTROLLER_ORIGIN,
    STANDARD_CONTROLLER_ORIGIN_COORD,
    STANDARD_CONTROLLER_TARGET,
    STANDARD_CONTROLLER_TARGET_COORD,
    StandardControllerHarness,
)

pytestmark = pytest.mark.unit


def test_right_click_same_square_requests_circle_removal() -> None:
    """Request user-circle removal only when right-click deletion is released.

    The controller should start delete mode on press, then commit a circle
    removal for same-square release and clear preview state around the flow.
    """
    harness = StandardControllerHarness()

    press_result = harness.controller.on_press(STANDARD_CONTROLLER_ORIGIN_COORD, button=MouseButton.RIGHT)
    release_result = harness.controller.on_release(STANDARD_CONTROLLER_ORIGIN_COORD, button=MouseButton.RIGHT)

    assert press_result == ControllerEventResult(handled=True, requires_render=True)
    assert release_result == ControllerEventResult(handled=True, requires_render=True)
    assert harness.annotation.calls == [
        ("clear_preview",),
        ("remove_circle", STANDARD_CONTROLLER_ORIGIN),
        ("clear_preview",),
    ]


def test_right_drag_requests_arrow_removal_without_preview() -> None:
    """Request user-arrow removal without rendering a delete preview.

    Pointer movement in delete mode should be consumed, but it must not call the
    preview methods used by annotation creation.
    """
    harness = StandardControllerHarness()

    press_result = harness.controller.on_press(STANDARD_CONTROLLER_ORIGIN_COORD, button=MouseButton.RIGHT)
    move_result = harness.controller.on_pointer_move(STANDARD_CONTROLLER_TARGET_COORD)
    release_result = harness.controller.on_release(STANDARD_CONTROLLER_TARGET_COORD, button=MouseButton.RIGHT)

    assert press_result == ControllerEventResult(handled=True, requires_render=True)
    assert move_result == ControllerEventResult(handled=True, requires_render=False)
    assert release_result == ControllerEventResult(handled=True, requires_render=True)
    assert harness.annotation.calls == [
        ("clear_preview",),
        ("remove_arrow", STANDARD_CONTROLLER_ORIGIN, STANDARD_CONTROLLER_TARGET),
        ("clear_preview",),
    ]


def test_right_click_delete_does_not_request_hint_arrow_removal() -> None:
    """Preserve hint arrows by never routing deletion to hint-arrow removal.

    Hint arrows share annotation rendering, but right-click deletion is only for
    user circles and arrows.
    """
    harness = StandardControllerHarness()

    harness.controller.on_press(STANDARD_CONTROLLER_ORIGIN_COORD, button=MouseButton.RIGHT)
    harness.controller.on_release(STANDARD_CONTROLLER_TARGET_COORD, button=MouseButton.RIGHT)

    assert not any(call[0] == "remove_hint_arrow" for call in harness.annotation.calls)


def test_left_click_annotation_creation_still_uses_modifier_preview_and_commit() -> None:
    """Create a primary circle through the left-click modifier path.

    Right-click deletion must not regress the existing flow where a modifier
    selects the annotation style and release commits the preview.
    """
    harness = StandardControllerHarness()

    press_result = harness.controller.on_press(
        STANDARD_CONTROLLER_ORIGIN_COORD, button=MouseButton.LEFT, modifier=Modifier.SHIFT
    )
    release_result = harness.controller.on_release(STANDARD_CONTROLLER_ORIGIN_COORD, button=MouseButton.LEFT)

    assert press_result == ControllerEventResult(handled=True, requires_render=True)
    assert release_result == ControllerEventResult(handled=True, requires_render=True)
    assert harness.annotation.calls == [
        ("set_circle_preview", CircleType.PRIMARY, STANDARD_CONTROLLER_ORIGIN),
        ("add_circle", CircleType.PRIMARY, STANDARD_CONTROLLER_ORIGIN),
        ("clear_preview",),
    ]


def test_right_click_delete_does_nothing_when_annotations_are_disabled() -> None:
    """Avoid annotation calls when annotation interaction is disabled.

    The controller may still query the square for routing, but it must not start
    delete mode or mutate annotation state.
    """
    harness = StandardControllerHarness(annotations_enabled=False)

    press_result = harness.controller.on_press(STANDARD_CONTROLLER_ORIGIN_COORD, button=MouseButton.RIGHT)
    release_result = harness.controller.on_release(STANDARD_CONTROLLER_ORIGIN_COORD, button=MouseButton.RIGHT)

    assert press_result == ControllerEventResult()
    assert release_result == ControllerEventResult()
    assert harness.annotation.calls == []


def test_right_click_delete_does_nothing_while_promotion_is_active() -> None:
    """Let active promotion flow take priority over annotation deletion.

    Promotion routing should stop right-click annotation deletion before square
    lookup or annotation cleanup can happen.
    """
    harness = StandardControllerHarness(promotion_active=True)

    press_result = harness.controller.on_press(STANDARD_CONTROLLER_ORIGIN_COORD, button=MouseButton.RIGHT)
    release_result = harness.controller.on_release(STANDARD_CONTROLLER_ORIGIN_COORD, button=MouseButton.RIGHT)

    assert press_result == ControllerEventResult()
    assert release_result == ControllerEventResult()
    assert harness.query.calls == []
    assert harness.annotation.calls == []
