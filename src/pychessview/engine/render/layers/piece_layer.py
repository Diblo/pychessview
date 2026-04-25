# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Piece rendering layer for the pychessview package."""

from ...core.state.piece_ui_state import PieceUiState
from ...layout.models.piece_layout import PieceLayout
from .base_layer import Layer


class PieceLayer(Layer[PieceUiState, PieceLayout]):
    """Rendering layer for chess pieces."""

    def render(self) -> None:
        """Render the layer using the active renderer and current layout state."""
        pieces = self.state.pieces()
        if not pieces:
            return

        self.layout.update()

        if self.state.preview_move is not None:
            promotion_from = self.state.preview_move.from_square
            promotion_to = self.state.preview_move.to_square
        else:
            promotion_from = None
            promotion_to = None

        drag_square = self.state.dragged_square
        drag_position = self.state.dragged_position
        drag_piece = None

        for square, piece in pieces.items():
            if square == drag_square:
                if drag_square is not None and drag_position is not None:
                    drag_piece = self.layout.drag_item(piece, drag_square, drag_position)
                    continue
            if square == promotion_from:
                if promotion_to is not None:
                    self.renderer.draw_square_image(self.layout.piece_item(piece, promotion_to))
                    continue
            if square == promotion_to:
                continue
            self.renderer.draw_square_image(self.layout.piece_item(piece, square))

        if drag_piece is not None:
            self.renderer.draw_square_image(drag_piece)
