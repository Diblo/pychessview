# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Annotation session implementation for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._helpers import ensure_no_active_promotion
from .protocols import AnnotationSessionProtocol

if TYPE_CHECKING:
    from ..annotation_types import ArrowType, CircleType, HintArrowType
    from ..primitives import Square
    from ..state.annotation_state import AnnotationState
    from ..state.promotion_state import PromotionState


class AnnotationSession(AnnotationSessionProtocol):
    """Coordinates annotation state updates."""

    __slots__ = "_annotation_state", "_promotion_state"

    _annotation_state: AnnotationState
    _promotion_state: PromotionState

    def __init__(self, annotation_state: AnnotationState, promotion_state: PromotionState) -> None:
        """Initialize the annotation session with its initial configuration.

        Args:
            annotation_state: State object used to initialize or update the annotation state.
            promotion_state: State object used to initialize or update the promotion state.
        """
        self._annotation_state = annotation_state
        self._promotion_state = promotion_state

    @classmethod
    def create(cls, annotation_state: AnnotationState, promotion_state: PromotionState) -> AnnotationSession:
        """Create an instance from the provided collaborators.

        Args:
            annotation_state: Annotation state to update.
            promotion_state: Promotion state to update.

        Returns:
            A newly created instance of ``cls``.
        """
        return cls(annotation_state, promotion_state)

    def set_circle_preview(self, circle_type: CircleType, square: Square) -> None:
        """Store the preview circle that should be rendered before it is committed.

        Args:
            circle_type: Circle annotation type to use.
            square: Square where the preview circle should be shown.
        """
        ensure_no_active_promotion(self._promotion_state, "set the circle preview")
        self._annotation_state.set_circle_preview(circle_type, square)

    def set_arrow_preview(
        self, arrow_type: ArrowType, from_square: Square, to_square: Square, has_corner: bool = False
    ) -> None:
        """Store the preview arrow that should be rendered before it is committed.

        Args:
            arrow_type: Arrow annotation type to use.
            from_square: Start square of the preview arrow.
            to_square: End square of the preview arrow.
            has_corner: Whether the arrow should include a corner.
        """
        ensure_no_active_promotion(self._promotion_state, "set the arrow preview")
        self._annotation_state.set_arrow_preview(arrow_type, from_square, to_square, has_corner)

    def clear_preview(self) -> None:
        """Clear any active annotation preview state."""
        self._annotation_state.clear_preview()

    def add_circle(self, circle_type: CircleType, square: Square) -> None:
        """Store a circle annotation for the given square.

        Args:
            circle_type: Circle annotation type to use.
            square: Square that should carry the circle annotation.
        """
        ensure_no_active_promotion(self._promotion_state, "add a circle annotation")
        self._annotation_state.add_circle(circle_type, square)

    def remove_circle(self, square: Square) -> None:
        """Remove the stored circle annotation for the given square.

        Args:
            square: Square whose circle annotation should be removed.
        """
        ensure_no_active_promotion(self._promotion_state, "remove a circle annotation")
        self._annotation_state.remove_circle(square)

    def clear_circles(self) -> None:
        """Remove all stored circle annotations."""
        self._annotation_state.clear_circles()

    def add_arrow(
        self, arrow_type: ArrowType, from_square: Square, to_square: Square, has_corner: bool = False
    ) -> None:
        """Store an arrow annotation between two squares.

        Args:
            arrow_type: Arrow annotation type to use.
            from_square: Start square of the arrow.
            to_square: End square of the arrow.
            has_corner: Whether the arrow should include a corner.
        """
        ensure_no_active_promotion(self._promotion_state, "add an arrow annotation")
        self._annotation_state.add_arrow(arrow_type, from_square, to_square, has_corner)

    def remove_arrow(self, from_square: Square, to_square: Square) -> None:
        """Remove the stored arrow annotation between two squares.

        Args:
            from_square: Start square of the stored arrow.
            to_square: End square of the stored arrow.
        """
        ensure_no_active_promotion(self._promotion_state, "remove an arrow annotation")
        self._annotation_state.remove_arrow(from_square, to_square)

    def clear_arrows(self) -> None:
        """Remove all stored arrow annotations."""
        self._annotation_state.clear_arrows()

    def add_hint_arrow(
        self, arrow_type: HintArrowType, from_square: Square, to_square: Square, has_corner: bool = False
    ) -> None:
        """Store a hint arrow between two squares.

        Args:
            arrow_type: Arrow annotation type to use.
            from_square: Start square of the hint arrow.
            to_square: End square of the hint arrow.
            has_corner: Whether the arrow should include a corner.
        """
        ensure_no_active_promotion(self._promotion_state, "add a hint arrow annotation")
        self._annotation_state.add_hint_arrow(arrow_type, from_square, to_square, has_corner)

    def remove_hint_arrow(self, from_square: Square, to_square: Square) -> None:
        """Remove the stored hint arrow between two squares.

        Args:
            from_square: Start square of the stored hint arrow.
            to_square: End square of the stored hint arrow.
        """
        ensure_no_active_promotion(self._promotion_state, "remove a hint arrow annotation")
        self._annotation_state.remove_hint_arrow(from_square, to_square)

    def clear_hint_arrows(self) -> None:
        """Remove all stored hint arrows."""
        self._annotation_state.clear_hint_arrows()
