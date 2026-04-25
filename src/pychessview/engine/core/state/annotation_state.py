# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Annotation state container for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import State

if TYPE_CHECKING:
    from ..annotation_types import ArrowType, CircleType, HintArrowType
    from ..primitives import Square


class AnnotationState(State):
    """Stores persistent and preview annotation state."""

    __slots__ = "_circle_preview", "_arrow_preview", "_circles", "_hint_arrows", "_arrows"

    _circle_preview: tuple[CircleType, Square] | None
    _arrow_preview: tuple[ArrowType, tuple[Square, Square, bool]] | None

    _circles: dict[Square, CircleType]
    _hint_arrows: dict[tuple[Square, Square], tuple[HintArrowType, bool]]
    _arrows: dict[tuple[Square, Square], tuple[ArrowType, bool]]

    def __init__(self) -> None:
        """Initialize the annotation state with its initial configuration."""
        self._circle_preview = None
        self._arrow_preview = None

        self._circles = {}
        self._hint_arrows = {}
        self._arrows = {}

    def get_circle_preview(self) -> tuple[CircleType, Square] | None:
        """Return the currently previewed circle annotation, if any.

        Returns:
            The preview circle as ``(circle_type, square)``, or ``None`` when no circle preview exists.
        """
        return self._circle_preview

    def set_circle_preview(self, annotation_type: CircleType, square: Square) -> None:
        """Store the preview circle that should be rendered before it is committed.

        Args:
            annotation_type: Circle annotation type to preview.
            square: Square where the preview circle should be shown.
        """
        self._circle_preview = (annotation_type, square)
        self._arrow_preview = None

    def get_arrow_preview(self) -> tuple[ArrowType, tuple[Square, Square, bool]] | None:
        """Return the currently previewed arrow annotation, if any.

        Returns:
            The preview arrow, or ``None`` when no arrow preview exists.
        """
        return self._arrow_preview

    def set_arrow_preview(
        self, annotation_type: ArrowType, square: Square, to_square: Square, has_corner: bool = False
    ) -> None:
        """Store the preview arrow that should be rendered before it is committed.

        Args:
            annotation_type: Arrow annotation type to preview.
            square: Start square of the preview arrow.
            to_square: End square of the preview arrow.
            has_corner: Whether the arrow should include a corner.
        """
        self._circle_preview = None
        self._arrow_preview = (annotation_type, (square, to_square, has_corner))

    def has_preview(self) -> bool:
        """Return whether a preview circle or arrow is currently active.

        Returns:
            ``True`` when either a circle preview or an arrow preview is stored.
        """
        return self._circle_preview is not None or self._arrow_preview is not None

    def clear_preview(self) -> None:
        """Clear any active annotation preview state."""
        self._circle_preview = None
        self._arrow_preview = None

    def get_circles(self) -> tuple[tuple[CircleType, Square], ...]:
        """Return all stored circle annotations as ``(circle_type, square)`` pairs.

        Returns:
            tuple[tuple[CircleType, Square], ...]: Stored circle annotations in mapping iteration order.
        """
        return tuple((circle_type, square) for square, circle_type in self._circles.items())

    def add_circle(self, circle_type: CircleType, square: Square) -> None:
        """Store a circle annotation for the given square.

        Args:
            circle_type: Circle annotation type to use.
            square: Square that should carry the circle annotation.
        """
        self._circles[square] = circle_type

    def remove_circle(self, square: Square) -> None:
        """Remove the stored circle annotation for the given square.

        Args:
            square: Square whose circle annotation should be removed.
        """
        self._circles.pop(square, None)

    def clear_circles(self) -> None:
        """Remove all stored circle annotations."""
        self._circles = {}

    def get_arrows(self) -> tuple[tuple[ArrowType, tuple[Square, Square], bool], ...]:
        """Return all stored arrow annotations as ``(arrow_type, (from_square, to_square), has_corner)`` tuples.

        Returns:
            ((ArrowType, (Square, Square), bool), ...): Stored arrow annotations in mapping iteration order.
        """
        return tuple((arrow_type, squares, has_corner) for squares, [arrow_type, has_corner] in self._arrows.items())

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
        self._arrows[(from_square, to_square)] = (arrow_type, has_corner)

    def remove_arrow(self, from_square: Square, to_square: Square) -> None:
        """Remove the stored arrow annotation between two squares.

        Args:
            from_square: Start square of the stored arrow.
            to_square: End square of the stored arrow.
        """
        self._arrows.pop((from_square, to_square), None)

    def clear_arrows(self) -> None:
        """Remove all stored arrow annotations."""
        self._arrows = {}

    def get_hint_arrows(self) -> tuple[tuple[HintArrowType, tuple[Square, Square], bool], ...]:
        """Return all stored hint arrows as ``(arrow_type, (from_square, to_square), has_corner)`` tuples.

        Returns:
            ((HintArrowType, (Square, Square), bool), ...): Stored hint arrows in mapping iteration order.
        """
        return tuple(
            (arrow_type, squares, has_corner) for squares, [arrow_type, has_corner] in self._hint_arrows.items()
        )

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
        self._hint_arrows[(from_square, to_square)] = (arrow_type, has_corner)

    def remove_hint_arrow(self, from_square: Square, to_square: Square) -> None:
        """Remove the stored hint arrow between two squares.

        Args:
            from_square: Start square of the stored hint arrow.
            to_square: End square of the stored hint arrow.
        """
        self._hint_arrows.pop((from_square, to_square), None)

    def clear_hint_arrows(self) -> None:
        """Remove all stored hint arrows."""
        self._hint_arrows = {}

    def has_annotation(self) -> bool:
        """Return whether any annotation or annotation preview is stored.

        Returns:
            ``True`` when any preview, circle, hint arrow, or arrow is currently stored.
        """
        return bool(self.has_preview() or self._circles or self._hint_arrows or self._arrows)

    def clear_all(self) -> None:
        """Clear all tracked session state."""
        self.clear_preview()
        self.clear_circles()
        self.clear_hint_arrows()
        self.clear_arrows()
