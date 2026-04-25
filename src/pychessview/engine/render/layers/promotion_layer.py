# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Promotion rendering layer for the pychessview package."""

from ...core.primitives import PlayerColor
from ...core.state.promotion_state import PromotionState
from ...layout.models.promotion_layout import PromotionLayout
from .base_layer import Layer


class PromotionLayer(Layer[PromotionState, PromotionLayout]):
    """Rendering layer for promotion choices."""

    def render(self) -> None:
        """Render the layer using the active renderer and current layout state."""
        if not self.state.is_active():
            return

        self.layout.update()

        if self.state.color == PlayerColor.WHITE:
            promotion_pieces = self.state.white_promotion_pieces
        else:
            promotion_pieces = self.state.black_promotion_pieces

        promotion_square = self.state.move.to_square

        for i, piece in enumerate(promotion_pieces):
            if self.state.highlighted == i:
                self.renderer.draw_square_color(self.layout.highlight_fill_item(promotion_square, i))
            else:
                self.renderer.draw_square_color(self.layout.fill_item(promotion_square, i))
            self.renderer.draw_square_image(self.layout.piece_item(promotion_square, i, piece))
