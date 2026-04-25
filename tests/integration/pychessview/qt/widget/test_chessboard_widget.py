# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Integration tests for Qt widget flows backed by the real pychessview view."""

from collections.abc import Iterator

import pytest

from tests.support.pychessview_api import (
    E2_E4_PLACEMENT,
    PROMOTED_QUEEN_PLACEMENT,
    PROMOTION_READY_FEN,
    STANDARD_START_FEN,
)
from tests.support.pychessview_qt_api import (
    create_standard_widget_harness,
    drag_piece,
    ensure_qapplication,
    image_has_visible_pixel,
    release_promotion_choice,
)

from .._helpers import ChessboardQtHarness, assert_widget_piece_placement, square

pytestmark = [pytest.mark.integration, pytest.mark.qt_integration, pytest.mark.requires_qt]


@pytest.fixture
def standard_widget_harness() -> Iterator[ChessboardQtHarness]:
    """Provide a real widget harness and clean up the Qt widget after the test.

    Yields:
        Harness around a real ``ChessboardWidget``.
    """
    harness = create_standard_widget_harness()
    try:
        yield harness
    finally:
        harness.widget.close()
        harness.widget.deleteLater()
        ensure_qapplication().processEvents()


def test_widget_mouse_input_moves_piece_through_real_view(
    standard_widget_harness: ChessboardQtHarness,
) -> None:
    """Widget mouse events should reach the controller and mutate the core game state.

    The flow uses the real widget, Qt adapter, controller, sessions, and adapter
    while still asserting only the observable FEN result.
    """
    drag_piece(standard_widget_harness, square("e", 2), square("e", 4))

    assert_widget_piece_placement(standard_widget_harness, E2_E4_PLACEMENT)


def test_widget_paint_flow_renders_to_in_memory_image(
    standard_widget_harness: ChessboardQtHarness,
) -> None:
    """Painting should integrate widget, renderer, and view without relying on pixel-perfect output.

    Rendering into an in-memory image verifies the real paint path can execute
    and produces visible output without depending on a display server.
    """
    image = standard_widget_harness.paint_to_image()

    assert image.width() == standard_widget_harness.width
    assert image.height() == standard_widget_harness.height
    assert image_has_visible_pixel(image) is True


def test_widget_controller_toggle_blocks_mouse_driven_move(
    standard_widget_harness: ChessboardQtHarness,
) -> None:
    """Disabling widget controller input should prevent normal board interaction.

    The widget forwards enablement to the core view, so a legal mouse drag must
    leave the FEN unchanged while interaction is disabled.
    """
    standard_widget_harness.widget.controller_enabled = False

    drag_piece(standard_widget_harness, square("e", 2), square("e", 4))

    assert standard_widget_harness.widget.fen == STANDARD_START_FEN


def test_widget_settings_delegation_updates_view_layout_behavior(
    standard_widget_harness: ChessboardQtHarness,
) -> None:
    """Settings changed through the widget should affect the underlying view layout.

    The widget exposes the view-owned settings object. Changing border and
    orientation through that facade must be reflected in public query behavior
    after the next paint.
    """
    standard_widget_harness.widget.settings.show_border = False
    standard_widget_harness.widget.settings.white_at_bottom = False
    standard_widget_harness.paint_to_image()

    assert standard_widget_harness.widget.query.square_at(0, standard_widget_harness.height - 1) == square("h", 8)


def test_widget_promotion_flow_applies_selected_piece() -> None:
    """Promotion should work through widget-level mouse input and the real Qt adapter.

    A promotion-ready position protects the collaboration between widget events,
    controller promotion state, promotion layout queries, and the final adapter
    update after selecting the queen option.
    """
    harness = create_standard_widget_harness(default_fen=PROMOTION_READY_FEN)
    try:
        drag_piece(harness, square("a", 7), square("a", 8))
        release_promotion_choice(harness, 0)

        assert_widget_piece_placement(harness, PROMOTED_QUEEN_PLACEMENT)
    finally:
        harness.widget.close()
        harness.widget.deleteLater()
