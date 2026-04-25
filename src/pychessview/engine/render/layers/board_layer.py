# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Board rendering layer for the pychessview package."""

from ...core.label_types import FileLabelSide, RankLabelSide
from ...core.primitives import SQUARES, File, Rank
from ...layout.models.board_layout import BoardLayout
from .base_layer import Layer


class BoardLayer(Layer[None, BoardLayout]):
    """Rendering layer for the board background and labels."""

    def render(self) -> None:
        """Render the layer using the active renderer and current layout state."""
        renderer = self.renderer
        view_state = self.view_state
        layout = self.layout

        layout.update()

        background_item = layout.background_item()
        if background_item:
            renderer.draw_square_color(background_item)

        renderer.draw_square_color(layout.board_item())

        for square in SQUARES:
            renderer.draw_square_image(layout.square_item(square))

        if view_state.show_labels:
            for side in FileLabelSide:
                if not view_state.is_label_side_visible(side):
                    continue
                for axis in File:
                    renderer.draw_text_ink(layout.label_item(side, axis))

            for side in RankLabelSide:
                if not view_state.is_label_side_visible(side):
                    continue
                for axis in Rank:
                    renderer.draw_text_ink(layout.label_item(side, axis))
