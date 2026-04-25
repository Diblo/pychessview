# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Highlight rendering layer for the pychessview package."""

from ...core.state.highlight_state import HighlightState
from ...layout.models.highlight_layout import HighlightLayout
from .base_layer import Layer


class HighlightLayer(Layer[HighlightState, HighlightLayout]):
    """Rendering layer for move and selection highlights."""

    def render(self) -> None:
        """Render the layer using the active renderer and current layout state."""
        if not self.state.has_highlights():
            return

        self.layout.update()

        # Last move
        last_move = self.state.get_last_move()
        if last_move is not None:
            self.renderer.draw_square_image(self.layout.last_move(last_move.from_square))
            self.renderer.draw_square_image(self.layout.last_move(last_move.to_square))

        # Check
        square = self.state.get_check()
        if square is not None:
            self.renderer.draw_square_image(self.layout.check(square))

        # Hints
        for highlight_player, style, square in self.state.get_hints():
            self.renderer.draw_square_image(self.layout.hint(highlight_player, style, square))

        # Selection
        selected = self.state.get_selected()
        if selected is not None:
            self.renderer.draw_square_image(self.layout.selected(*selected))
