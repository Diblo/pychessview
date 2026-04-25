# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for highlight state."""

import pytest

from pychessview.engine.core.highlight_types import HighlightPlayer, HintStyle
from pychessview.engine.core.primitives import File, Move, Rank, Square
from pychessview.engine.core.state.highlight_state import HighlightState

pytestmark = pytest.mark.unit


def test_highlight_state_tracks_move_check_selection_and_hints() -> None:
    """Store each highlight family independently until cleared.

    Last move, check, selection, and hints have different lifecycles. The state
    container must keep them separate so interaction cleanup does not erase game
    status highlights.
    """
    state = HighlightState()
    move = Move(Square(File.A, Rank.TWO), Square(File.A, Rank.FOUR))
    check_square = Square(File.E, Rank.ONE)
    selected_square = Square(File.B, Rank.ONE)
    hint_square = Square(File.C, Rank.THREE)

    state.set_last_move(move)
    state.set_check(check_square)
    state.set_selected(HighlightPlayer.PLAYER, selected_square)
    state.add_hint(HighlightPlayer.OPPONENT, HintStyle.PSEUDO_HINT, hint_square)

    assert state.get_last_move() == move
    assert state.get_check() == check_square
    assert state.get_selected() == (HighlightPlayer.PLAYER, selected_square)
    assert state.get_hints() == ((HighlightPlayer.OPPONENT, HintStyle.PSEUDO_HINT, hint_square),)
    assert state.has_highlights() is True


def test_highlight_state_interaction_clear_preserves_game_status_highlights() -> None:
    """Clear only selection and hints for interaction cleanup.

    Cancelling pointer interaction should not erase last-move or check
    indicators that belong to the current board position.
    """
    state = HighlightState()
    move = Move(Square(File.A, Rank.TWO), Square(File.A, Rank.FOUR))
    check_square = Square(File.E, Rank.ONE)

    state.set_last_move(move)
    state.set_check(check_square)
    state.set_selected(HighlightPlayer.PLAYER, Square(File.A, Rank.TWO))
    state.set_hints(HighlightPlayer.PLAYER, ((HintStyle.HINT, Square(File.A, Rank.THREE)),))

    state.clear_interaction()

    assert state.get_last_move() == move
    assert state.get_check() == check_square
    assert state.get_selected() is None
    assert state.get_hints() == ()


def test_highlight_state_clear_all_removes_every_highlight() -> None:
    """Return all highlight state to an empty baseline.

    Board reset and game reload flows need one operation that clears both
    position-status highlights and interaction-only highlights.
    """
    state = HighlightState()

    state.set_last_move(Move(Square(File.A, Rank.TWO), Square(File.A, Rank.FOUR)))
    state.set_check(Square(File.E, Rank.ONE))
    state.set_selected(HighlightPlayer.PLAYER, Square(File.A, Rank.TWO))
    state.add_hint(HighlightPlayer.PLAYER, HintStyle.HINT, Square(File.A, Rank.THREE))
    state.clear_all()

    assert state.get_last_move() is None
    assert state.get_check() is None
    assert state.get_selected() is None
    assert state.get_hints() == ()
    assert state.has_highlights() is False
