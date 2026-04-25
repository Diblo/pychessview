# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for render layer command emission."""

from typing import Any, cast

import pytest

from pychessview.engine.core.annotation_types import ArrowType, CircleType, HintArrowType
from pychessview.engine.core.highlight_types import HighlightPlayer, HintStyle
from pychessview.engine.core.primitives import File, Move, Piece, PieceKind, PlayerColor, Rank, Square
from pychessview.engine.core.state.annotation_state import AnnotationState
from pychessview.engine.core.state.highlight_state import HighlightState
from pychessview.engine.core.state.promotion_state import PromotionState
from pychessview.engine.core.state.view_state import ViewState
from pychessview.engine.layout.primitives import Color
from pychessview.engine.render.layers.annotation_layer import AnnotationLayer
from pychessview.engine.render.layers.board_layer import BoardLayer
from pychessview.engine.render.layers.highlight_layer import HighlightLayer
from pychessview.engine.render.layers.piece_layer import PieceLayer
from pychessview.engine.render.layers.promotion_layer import PromotionLayer
from pychessview.engine.render.renderer.null_renderer import (
    DrawArrowCommand,
    DrawCircleCommand,
    DrawSquareColorCommand,
    DrawSquareImageCommand,
    DrawTextInkCommand,
    NullRenderer,
)

from ..._helpers import (
    AnnotationLayoutSpy,
    BoardLayoutSpy,
    HighlightLayoutSpy,
    PieceLayoutSpy,
    PieceStateStub,
    PromotionLayoutSpy,
    image_paths,
)

pytestmark = pytest.mark.unit


def test_board_layer_renders_background_board_squares_and_visible_labels_in_order() -> None:
    """Emit board commands in the order consumed by renderers.

    The board layer should refresh layout once, draw background before the board
    surface, then draw all square textures before visible labels.
    """
    view_state = ViewState(PlayerColor.WHITE)
    renderer = NullRenderer()
    layout = BoardLayoutSpy()
    layer = BoardLayer(view_state, None, renderer, cast(Any, layout))

    layer.render()

    assert layout.update_calls == 1
    assert [type(command) for command in renderer.commands[:2]] == [DrawSquareColorCommand, DrawSquareColorCommand]
    background_command = renderer.commands[0]
    board_command = renderer.commands[1]
    assert isinstance(background_command, DrawSquareColorCommand)
    assert isinstance(board_command, DrawSquareColorCommand)
    assert background_command.item.color == Color(1, 1, 1)
    assert board_command.item.color == Color(2, 2, 2)
    assert all(isinstance(command, DrawSquareImageCommand) for command in renderer.commands[2:66])
    assert all(isinstance(command, DrawTextInkCommand) for command in renderer.commands[66:])
    assert len(renderer.commands[2:66]) == 64
    assert len(renderer.commands[66:]) == 16


def test_annotation_layer_renders_hints_user_annotations_and_preview_in_order() -> None:
    """Render annotation groups in the order expected by visual stacking.

    Hint arrows render below user annotations, and previews render after stored
    annotations so the in-progress interaction remains visible.
    """
    renderer = NullRenderer()
    state = AnnotationState()
    layout = AnnotationLayoutSpy()
    layer = AnnotationLayer(ViewState(PlayerColor.WHITE), state, renderer, cast(Any, layout))
    from_square = Square(File.A, Rank.ONE)
    to_square = Square(File.H, Rank.EIGHT)

    state.add_hint_arrow(HintArrowType.PRIMARY, from_square, to_square)
    state.add_circle(CircleType.PRIMARY, from_square)
    state.add_arrow(ArrowType.SECONDARY, from_square, to_square)
    state.set_circle_preview(CircleType.ALTERNATIVE, to_square)

    layer.render()

    assert layout.update_calls == 1
    assert [type(command) for command in renderer.commands] == [
        DrawArrowCommand,
        DrawCircleCommand,
        DrawArrowCommand,
        DrawCircleCommand,
    ]
    assert layout.arrow_calls == [
        (HintArrowType.PRIMARY, from_square, to_square, False),
        (ArrowType.SECONDARY, from_square, to_square, False),
    ]
    assert layout.circle_calls == [(CircleType.PRIMARY, from_square), (CircleType.ALTERNATIVE, to_square)]


def test_highlight_layer_renders_each_active_highlight_family_in_stable_order() -> None:
    """Render move, check, hints, and selection highlights in stable order.

    Stable ordering matters because later highlight images can visually overlay
    earlier ones on the same square.
    """
    renderer = NullRenderer()
    state = HighlightState()
    layout = HighlightLayoutSpy()
    layer = HighlightLayer(ViewState(PlayerColor.WHITE), state, renderer, cast(Any, layout))
    move = Move(Square(File.E, Rank.TWO), Square(File.E, Rank.FOUR))

    state.set_last_move(move)
    state.set_check(Square(File.E, Rank.ONE))
    state.add_hint(HighlightPlayer.PLAYER, HintStyle.HINT, Square(File.E, Rank.THREE))
    state.set_selected(HighlightPlayer.PLAYER, Square(File.E, Rank.TWO))

    layer.render()

    assert layout.update_calls == 1
    assert image_paths(renderer) == [
        "last:E2",
        "last:E4",
        "check:E1",
        "hint:player:hint:E3",
        "selected:player:E2",
    ]


def test_piece_layer_skips_original_drag_square_and_renders_dragged_piece_last() -> None:
    """Render dragged pieces above normal board pieces.

    The original square for the dragged piece should not emit a normal piece
    image while the drag preview is active.
    """
    renderer = NullRenderer()
    state = PieceStateStub()
    layout = PieceLayoutSpy()
    layer = PieceLayer(ViewState(PlayerColor.WHITE), cast(Any, state), renderer, cast(Any, layout))

    layer.render()

    assert layout.update_calls == 1
    assert image_paths(renderer) == ["piece:king:A1", "drag:pawn"]
    drag_command = renderer.commands[-1]
    assert isinstance(drag_command, DrawSquareImageCommand)
    assert drag_command.item.rect.center == state.dragged_position


def test_promotion_layer_renders_fill_and_piece_for_each_option() -> None:
    """Render every promotion option with highlighted fill for the active index.

    The layer alternates fill and piece commands so each option background is
    drawn before the piece occupying that option.
    """
    renderer = NullRenderer()
    state = PromotionState(
        (
            Piece(PlayerColor.WHITE, PieceKind.QUEEN),
            Piece(PlayerColor.WHITE, PieceKind.ROOK),
            Piece(PlayerColor.WHITE, PieceKind.BISHOP),
            Piece(PlayerColor.WHITE, PieceKind.KNIGHT),
        ),
        (),
    )
    layout = PromotionLayoutSpy()
    layer = PromotionLayer(ViewState(PlayerColor.WHITE), state, renderer, cast(Any, layout))

    state.show_promotion(Move(Square(File.A, Rank.SEVEN), Square(File.A, Rank.EIGHT)), PlayerColor.WHITE)
    state.set_highlight(1)
    layer.render()

    assert layout.update_calls == 1
    assert [type(command) for command in renderer.commands] == [
        DrawSquareColorCommand,
        DrawSquareImageCommand,
        DrawSquareColorCommand,
        DrawSquareImageCommand,
        DrawSquareColorCommand,
        DrawSquareImageCommand,
        DrawSquareColorCommand,
        DrawSquareImageCommand,
    ]
    assert [command.item.color for command in renderer.commands if isinstance(command, DrawSquareColorCommand)] == [
        Color(0, 0, 0),
        Color(99, 1, 0),
        Color(2, 0, 0),
        Color(3, 0, 0),
    ]
    assert image_paths(renderer) == [
        "promotion:0:queen",
        "promotion:1:rook",
        "promotion:2:bishop",
        "promotion:3:knight",
    ]
