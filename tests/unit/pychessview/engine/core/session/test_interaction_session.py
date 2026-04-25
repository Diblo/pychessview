# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for interaction session behavior."""

from __future__ import annotations

import pytest

from pychessview.engine.core.exceptions import PieceNotFoundError
from pychessview.engine.core.highlight_types import HighlightPlayer, HintStyle
from pychessview.engine.core.primitives import Piece, PieceKind, PlayerColor, Square, SquareData
from pychessview.engine.layout.primitives import Coord

from ..._helpers import SessionAdapterStub, create_interaction_session

pytestmark = pytest.mark.unit


def test_interaction_session_selects_player_piece_and_sets_legal_hints() -> None:
    """Select player-owned pieces and classify empty versus occupied legal destinations."""
    adapter = SessionAdapterStub()
    origin = Square(0, 0)
    empty_target = Square(1, 0)
    occupied_target = Square(2, 0)
    adapter.placement[origin] = Piece(PlayerColor.WHITE, PieceKind.KNIGHT)
    adapter.placement[occupied_target] = Piece(PlayerColor.BLACK, PieceKind.PAWN)
    adapter.legal_hints[origin] = {empty_target, occupied_target}
    session, highlight_state, _, _, _ = create_interaction_session(adapter)

    session.select_piece(origin)

    assert highlight_state.get_selected() == (HighlightPlayer.PLAYER, origin)
    assert set(highlight_state.get_hints()) == {
        (HighlightPlayer.PLAYER, HintStyle.HINT, empty_target),
        (HighlightPlayer.PLAYER, HintStyle.OCCUPIED, occupied_target),
    }


def test_interaction_session_selects_pseudo_hints_when_piece_does_not_have_turn() -> None:
    """Use pseudo-legal hints when inspecting a piece that is not allowed to move now."""
    adapter = SessionAdapterStub()
    origin = Square(0, 0)
    target = Square(1, 0)
    adapter.turn = PlayerColor.BLACK
    adapter.placement[origin] = Piece(PlayerColor.WHITE, PieceKind.BISHOP)
    adapter.pseudo_hints[origin] = {target}
    session, highlight_state, _, _, _ = create_interaction_session(adapter)

    session.select_piece(origin)

    assert highlight_state.get_selected() == (HighlightPlayer.PLAYER, origin)
    assert highlight_state.get_hints() == ((HighlightPlayer.PLAYER, HintStyle.PSEUDO_HINT, target),)


def test_interaction_session_returns_selected_square_data_only_while_piece_exists() -> None:
    """Expose selected piece data and drop stale selections when the board square becomes empty."""
    adapter = SessionAdapterStub()
    origin = Square(0, 0)
    piece = Piece(PlayerColor.WHITE, PieceKind.ROOK)
    adapter.placement[origin] = piece
    session, highlight_state, _, _, _ = create_interaction_session(adapter)
    highlight_state.set_selected(HighlightPlayer.PLAYER, origin)

    assert session.get_selected() == SquareData(origin, piece)

    adapter.placement.clear()
    assert session.get_selected() is None
    assert session.has_active_selection() is False


def test_interaction_session_rejects_selection_and_drag_from_empty_square() -> None:
    """Fail fast when callers try to select or drag a square without a piece."""
    adapter = SessionAdapterStub()
    session, _, _, _, _ = create_interaction_session(adapter)

    with pytest.raises(PieceNotFoundError, match="select empty square"):
        session.select_piece(Square(0, 0))
    with pytest.raises(PieceNotFoundError, match="drag piece from empty square"):
        session.begin_drag(Square(0, 0), Coord(1, 2))


def test_interaction_session_updates_and_clears_active_drag_state() -> None:
    """Track drag position only while a dragged piece is active and still present."""
    adapter = SessionAdapterStub()
    origin = Square(0, 0)
    adapter.placement[origin] = Piece(PlayerColor.WHITE, PieceKind.KNIGHT)
    session, _, piece_ui_state, _, _ = create_interaction_session(adapter)

    session.begin_drag(origin, Coord(1, 2))
    session.update_drag(Coord(3, 4))

    assert session.has_active_drag() is True
    assert piece_ui_state.dragged_square == origin
    assert piece_ui_state.dragged_position == Coord(3, 4)

    session.clear_drag()
    assert session.has_active_drag() is False
