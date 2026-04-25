# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Private helpers for pychessview session logic."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..exceptions import ChessboardViewError
from ..highlight_types import HighlightPlayer, HintStyle

if TYPE_CHECKING:
    from ..domain.adapters.protocol import GameAdapterProtocol
    from ..primitives import Move, Square
    from ..state.annotation_state import AnnotationState
    from ..state.highlight_state import HighlightState
    from ..state.piece_ui_state import PieceUiState
    from ..state.promotion_state import PromotionState
    from ..state.view_state import ViewState


def ensure_no_active_promotion(promotion_state: PromotionState, action: str) -> None:
    """Raise if a promotion chooser is currently active.

    Args:
        promotion_state: Value supplied for ``promotion_state``.
        action: String value supplied for ``action``.
    """
    if promotion_state.is_active():
        raise ChessboardViewError(f"cannot {action} while promotion is active")


def clear_interaction_state(
    highlight_state: HighlightState,
    piece_ui_state: PieceUiState,
    promotion_state: PromotionState,
    annotation_state: AnnotationState,
) -> None:
    """Clear transient interaction state.

    Args:
        highlight_state: Highlight state to update.
        piece_ui_state: Piece UI state to update.
        promotion_state: Promotion state to update.
        annotation_state: Annotation state to update.
    """
    highlight_state.clear_interaction()
    piece_ui_state.clear_all()
    promotion_state.clear_all()
    annotation_state.clear_preview()


def clear_all(
    highlight_state: HighlightState,
    piece_ui_state: PieceUiState,
    promotion_state: PromotionState,
    annotation_state: AnnotationState,
) -> None:
    """Clear all tracked session state.

    Args:
        highlight_state: Highlight state to update.
        piece_ui_state: Piece UI state to update.
        promotion_state: Promotion state to update.
        annotation_state: Annotation state to update.
    """
    highlight_state.clear_all()
    piece_ui_state.clear_all()
    promotion_state.clear_all()
    annotation_state.clear_all()


def update_highlight(
    game_adapter: GameAdapterProtocol, highlight_state: HighlightState, move: Move | None = None
) -> None:
    """Update highlight state from the current game state.

    Args:
        game_adapter: Game adapter to use.
        highlight_state: Highlight state to update.
        move: Last move to highlight, or ``None`` to clear the last-move highlight.
    """
    if move is not None:
        highlight_state.set_last_move(move)
    else:
        highlight_state.clear_last_move()

    if not (game_adapter.is_check() or game_adapter.is_checkmate()):
        highlight_state.clear_check()
        return

    king_square = game_adapter.king(game_adapter.turn)
    if king_square is not None:
        highlight_state.set_check(king_square)


def set_hints(
    view_state: ViewState, game_adapter: GameAdapterProtocol, highlight_state: HighlightState, square: Square
) -> None:
    """Set legal move hints for a square.

    Args:
        view_state: View state to use.
        game_adapter: Game adapter to use.
        highlight_state: Highlight state to update.
        square: Square whose legal destination hints should be computed.
    """
    piece = game_adapter.piece_at(square)
    if piece is None:
        return

    if piece.color is view_state.player:
        highlight_player = HighlightPlayer.PLAYER
    else:
        highlight_player = HighlightPlayer.OPPONENT

    hints: list[tuple[HintStyle, Square]] = []
    for hint_square in game_adapter.get_legal_hints(square):
        if game_adapter.piece_at(hint_square) is None:
            hints.append((HintStyle.HINT, hint_square))
        else:
            hints.append((HintStyle.OCCUPIED, hint_square))

    highlight_state.set_hints(highlight_player, tuple(hints))


def set_pseudo_hints(
    view_state: ViewState, game_adapter: GameAdapterProtocol, highlight_state: HighlightState, square: Square
) -> None:
    """Set pseudo-legal move hints for a square.

    Args:
        view_state: View state to use.
        game_adapter: Game adapter to use.
        highlight_state: Highlight state to update.
        square: Square whose pseudo-legal destination hints should be computed.
    """
    piece = game_adapter.piece_at(square)
    if piece is None:
        return

    if piece.color is view_state.player:
        highlight_player = HighlightPlayer.PLAYER
    else:
        highlight_player = HighlightPlayer.OPPONENT

    hints: list[tuple[HintStyle, Square]] = []
    for hint_square in game_adapter.get_pseudo_legal_hints(square, piece.color):
        if game_adapter.piece_at(hint_square) is None:
            hints.append((HintStyle.PSEUDO_HINT, hint_square))
        else:
            hints.append((HintStyle.PSEUDO_OCCUPIED, hint_square))

    highlight_state.set_hints(highlight_player, tuple(hints))
