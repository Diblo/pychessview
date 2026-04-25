# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Annotation rendering layer for the pychessview package."""

from ...core.state.annotation_state import AnnotationState
from ...layout.models.annotation_layout import AnnotationLayout
from .base_layer import Layer


class AnnotationLayer(Layer[AnnotationState, AnnotationLayout]):
    """Rendering layer for annotations."""

    def render(self) -> None:
        """Render the layer using the active renderer and current layout state."""
        state = self.state
        if not state.has_annotation():
            return

        renderer = self.renderer
        layout = self.layout

        layout.update()

        for arrow_type, (from_square, to_square), has_corner in state.get_hint_arrows():
            renderer.draw_arrow(*layout.arrow(arrow_type, from_square, to_square, has_corner))

        for circle_type, square in state.get_circles():
            renderer.draw_circle(*layout.circle(circle_type, square))

        for arrow_type, (from_square, to_square), has_corner in state.get_arrows():
            renderer.draw_arrow(*layout.arrow(arrow_type, from_square, to_square, has_corner))

        circle_preview = state.get_circle_preview()
        if circle_preview is not None:
            renderer.draw_circle(*layout.circle(*circle_preview))
            return

        arrow_preview = state.get_arrow_preview()
        if arrow_preview is not None:
            preview_type, preview_data = arrow_preview
            renderer.draw_arrow(*layout.arrow(preview_type, *preview_data))
