# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Arrow item render item definitions for the pychessview package."""

from .base import Item


class ArrowItem(Item):
    """Renderable item describing an arrow annotation.

    Attributes:
        shaft_width: Arrow shaft width in pixels.
        head_length: Arrow head length in pixels.
        head_width: Arrow head width in pixels.
    """

    __slots__ = "shaft_width", "head_length", "head_width"

    shaft_width: int
    head_length: int
    head_width: int

    def __init__(self, shaft_width: int, head_length: int, head_width: int) -> None:
        """Initialize the arrow item with its initial configuration.

        Args:
            shaft_width: Value used to initialize ``shaft_width``.
            head_length: Value used to initialize ``head_length``.
            head_width: Value used to initialize ``head_width``.
        """
        self.shaft_width = shaft_width
        self.head_length = head_length
        self.head_width = head_width

    def __copy__(self) -> "ArrowItem":
        """Return a shallow copy of the instance.

        Returns:
            Shallow copy of the instance.
        """
        return type(self)(self.shaft_width, self.head_length, self.head_width)
