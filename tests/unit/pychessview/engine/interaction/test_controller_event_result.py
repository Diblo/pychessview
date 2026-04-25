# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for controller event result value objects."""

import pytest

from pychessview.engine.interaction.controller_event_result import ControllerEventResult

pytestmark = pytest.mark.unit


def test_controller_event_result_defaults_are_neutral() -> None:
    """Represent ignored input without forcing consumers to branch around ``None``.

    A neutral result is used by controller adapters when no controller action should be consumed or rendered.
    """
    result = ControllerEventResult()

    assert result.handled is False
    assert result.requires_render is False


def test_controller_event_result_preserves_explicit_flags() -> None:
    """Expose controller decisions as immutable boolean flags for widget adapters."""
    result = ControllerEventResult(handled=True, requires_render=True)

    assert result.handled is True
    assert result.requires_render is True


def test_controller_event_result_compares_by_value() -> None:
    """Allow tests and adapters to compare event outcomes by contract rather than identity."""
    result = ControllerEventResult(handled=True, requires_render=False)

    assert result == ControllerEventResult(handled=True, requires_render=False)
    assert result != ControllerEventResult(handled=False, requires_render=False)
    assert result != object()
    assert hash(result) == hash(ControllerEventResult(handled=True, requires_render=False))


def test_controller_event_result_repr_includes_both_flags() -> None:
    """Keep failure output useful when an adapter propagates the wrong controller result."""
    result = ControllerEventResult(handled=True, requires_render=False)

    assert repr(result) == "ControllerEventResult(handled=True, requires_render=False)"


def test_controller_event_result_existing_slots_are_immutable() -> None:
    """Prevent post-construction mutation of the event outcome consumed by GUI adapters."""
    result = ControllerEventResult(handled=True)

    with pytest.raises(AttributeError, match="immutable"):
        result._handled = False  # pyright: ignore[reportPrivateUsage]
