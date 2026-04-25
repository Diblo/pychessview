# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Integration tests for public pychessview view flows."""

import pytest

from pychessview.engine.layout.primitives import Coord
from tests.support.pychessview_api import (
    BLACK_TO_MOVE_KINGS_ONLY_FEN,
    E2_E4_PLACEMENT,
    KINGS_ONLY_FEN,
    PROMOTED_QUEEN_PLACEMENT,
    PROMOTION_READY_FEN,
    STANDARD_START_FEN,
    create_arrow_annotation,
    create_circle_annotation,
    create_standard_game_spec,
    create_standard_harness,
    delete_arrow_annotation,
    delete_circle_annotation,
    drag_piece,
    release_promotion_choice,
    rendered_arrow_count,
    rendered_circle_count,
    rendered_label_texts,
)

from ._helpers import (
    assert_piece_placement,
    square,
)

pytestmark = [pytest.mark.integration, pytest.mark.requires_python_chess]


def test_standard_view_move_updates_fen_and_can_render_after_state_change() -> None:
    """Move input should collaborate through controller, sessions, adapter, and renderer.

    A legal e2-e4 drag exercises the real view wiring from pointer interaction
    through game mutation. Rendering afterwards protects against stale layout or
    session state after the move has changed the board.
    """
    harness = create_standard_harness()

    drag_piece(harness, square("e", 2), square("e", 4))

    assert_piece_placement(harness, E2_E4_PLACEMENT)
    assert harness.render()[-1].kind == "end_frame"


def test_promotion_flow_activates_choice_ui_and_commits_selected_piece() -> None:
    """Promotion should pause the move, show choices, and apply the selected piece.

    The flow verifies collaboration between the controller, promotion session,
    board query, adapter legality checks, and final board-state update.
    """
    harness = create_standard_harness(default_fen=PROMOTION_READY_FEN)

    drag_piece(harness, square("a", 7), square("a", 8))

    assert harness.view.game.fen == PROMOTION_READY_FEN
    assert harness.view.query.promotion_index_at(*_as_xy(harness.coord_for_promotion_index(0))) == 0

    release_promotion_choice(harness, 0)

    assert_piece_placement(harness, PROMOTED_QUEEN_PLACEMENT)
    assert harness.view.query.promotion_index_at(*_as_xy(harness.coord_for_square(square("a", 8)))) is None


def test_controller_disabled_blocks_equivalent_move_input() -> None:
    """Disabling the controller should swap input handling without mutating game state.

    The same legal drag that changes the board while enabled must be a no-op
    when controller input is disabled through the public view property.
    """
    enabled = create_standard_harness()
    disabled = create_standard_harness()
    disabled.view.controller_enabled = False

    drag_piece(enabled, square("e", 2), square("e", 4))
    drag_piece(disabled, square("e", 2), square("e", 4))

    assert_piece_placement(enabled, E2_E4_PLACEMENT)
    assert disabled.view.fen == STANDARD_START_FEN


def test_annotation_flow_creates_renders_and_deletes_user_annotations() -> None:
    """Circle and arrow annotations should be visible after creation and gone after deletion.

    This protects the real controller/session/render collaboration for both
    annotation shapes, including right-click deletion without affecting unrelated
    game state.
    """
    harness = create_standard_harness()

    create_circle_annotation(harness, square("e", 4))
    create_arrow_annotation(harness, square("b", 1), square("c", 3))

    assert rendered_circle_count(harness) == 1
    assert rendered_arrow_count(harness) == 1

    delete_circle_annotation(harness, square("e", 4))
    delete_arrow_annotation(harness, square("b", 1), square("c", 3))

    assert rendered_circle_count(harness) == 0
    assert rendered_arrow_count(harness) == 0
    assert harness.view.fen == STANDARD_START_FEN


def test_presentation_settings_change_observable_layout_and_label_rendering() -> None:
    """Selected presentation settings should affect rendered labels and coordinate mapping.

    The test samples high-value settings rather than every combination: labels
    must control text rendering, borders must reserve non-square space, and
    orientation must change which square appears at a fixed board corner.
    """
    harness = create_standard_harness(width=480, height=480)

    assert "1" in rendered_label_texts(harness)
    assert harness.view.query.square_at(0, 0) is None

    harness.view.settings.show_labels = False
    assert rendered_label_texts(harness) == ()

    harness.view.settings.show_border = False
    harness.render()
    assert harness.view.query.square_at(0, 0) == square("a", 8)
    assert harness.view.query.square_at(0, harness.height - 1) == square("a", 1)

    harness.view.settings.white_at_bottom = False
    harness.render()
    assert harness.view.query.square_at(0, harness.height - 1) == square("h", 8)


def test_load_reset_and_load_game_flow_keeps_fen_state_consistent() -> None:
    """Position loading and game replacement should reset to the requested source of truth.

    The flow protects the public view methods that replace adapter state,
    reset to defaults, reset to explicit FEN values, and rebuild game-specific
    runtime collaborators through ``load_game``.
    """
    harness = create_standard_harness(default_fen=KINGS_ONLY_FEN)

    harness.view.load_position_from_fen(STANDARD_START_FEN)
    assert harness.view.fen == STANDARD_START_FEN

    harness.view.reset_board()
    assert harness.view.fen == KINGS_ONLY_FEN

    harness.view.reset_board(BLACK_TO_MOVE_KINGS_ONLY_FEN)
    assert harness.view.fen == BLACK_TO_MOVE_KINGS_ONLY_FEN

    harness.view.load_game(create_standard_game_spec(PROMOTION_READY_FEN))
    assert harness.view.fen == PROMOTION_READY_FEN


def _as_xy(coord: Coord) -> tuple[int, int]:
    """Return a coordinate as an ``(x, y)`` tuple for query calls."""
    return (coord.x, coord.y)
