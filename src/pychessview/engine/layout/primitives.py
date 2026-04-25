# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Layout primitive types for the pychessview package.

Constants:
    NULL_RECT: Zero-sized rectangle used as a reusable empty layout placeholder.
"""

from __future__ import annotations

from collections.abc import Mapping
from enum import IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final, TypeAlias

ColorMapping: TypeAlias = Mapping[str, int]
"""Type alias for parsed RGBA color mappings."""


class VerticalAlign(IntEnum):
    """Enumeration of supported vertical alignments.

    Attributes:
        TOP: Top alignment or label side.
        CENTER: Centered alignment.
        BOTTOM: Bottom alignment or label side.
    """

    TOP = 0
    CENTER = 1
    BOTTOM = 2

    def __str__(self) -> str:
        """Return a human-readable representation of the instance.

        Returns:
            Human-readable representation of the instance.
        """
        return self.name.lower()

    def __repr__(self) -> str:
        """Return a developer-oriented representation of the instance.

        Returns:
            Developer-oriented representation of the instance.
        """
        return f"VerticalAlign({self.name}={self.value})"


class HorizontalAlign(IntEnum):
    """Enumeration of supported horizontal alignments.

    Attributes:
        LEFT: Left alignment or label side.
        CENTER: Centered alignment.
        RIGHT: Right alignment or label side.
    """

    LEFT = 0
    CENTER = 1
    RIGHT = 2

    def __str__(self) -> str:
        """Return a human-readable representation of the instance.

        Returns:
            Human-readable representation of the instance.
        """
        return self.name.lower()

    def __repr__(self) -> str:
        """Return a developer-oriented representation of the instance.

        Returns:
            Developer-oriented representation of the instance.
        """
        return f"HorizontalAlign({self.name}={self.value})"


class Arrow:
    """Stores arrow geometry factors used during rendering.

    Attributes:
        shaft_width: Arrow shaft width in pixels.
        head_length: Arrow head length in pixels.
        head_width: Arrow head width in pixels.
    """

    __slots__ = "shaft_width", "head_length", "head_width"

    shaft_width: Final[float]
    head_length: Final[float]
    head_width: Final[float]

    def __init__(self, shaft_width: float, head_length: float, head_width: float) -> None:
        """Initialize the arrow with its initial configuration.

        Args:
            shaft_width: Value used to initialize ``shaft_width``.
            head_length: Value used to initialize ``head_length``.
            head_width: Value used to initialize ``head_width``.
        """
        self.shaft_width = shaft_width
        self.head_length = head_length
        self.head_width = head_width

    def __eq__(self, other: object) -> bool:
        """Return whether ``other`` represents the same value as this instance.

        Args:
            other: Object to compare against this instance.

        Returns:
            ``True`` when ``other`` represents the same value as this instance; otherwise, ``False``.
        """
        if not isinstance(other, Arrow):
            return False
        return (
            self.shaft_width == other.shaft_width
            and self.head_length == other.head_length
            and self.head_width == other.head_width
        )

    def __str__(self) -> str:
        """Return a human-readable representation of the instance.

        Returns:
            Human-readable representation of the instance.
        """
        return f"Arrow(shaft_width={self.shaft_width}, head_length={self.head_length}, head_width={self.head_width})"

    __repr__ = __str__


class Color:
    """Represents an RGBA color.

    Attributes:
        r: Red channel value.
        g: Green channel value.
        b: Blue channel value.
        a: Alpha channel value.
    """

    __slots__ = "r", "g", "b", "a"

    r: Final[int]
    g: Final[int]
    b: Final[int]
    a: Final[int]

    def __init__(self, r: int, g: int, b: int, a: int | None = None) -> None:
        """Initialize the color with its initial configuration.

        Args:
            r: Value used to initialize ``r``.
            g: Value used to initialize ``g``.
            b: Value used to initialize ``b``.
            a: Value used to initialize ``a``.
        """
        self.r = r
        self.g = g
        self.b = b
        self.a = a if a is not None else 255

    @staticmethod
    def from_mapping(data: ColorMapping) -> Color:
        """Create an instance from a mapping of field names to values.

        Args:
            data: Parsed input data.

        Returns:
            A new instance populated from the mapping values.
        """
        return Color(r=data["r"], g=data["g"], b=data["b"], a=data.get("a", 255))

    def __eq__(self, other: object) -> bool:
        """Return whether ``other`` represents the same value as this instance.

        Args:
            other: Object to compare against this instance.

        Returns:
            ``True`` when ``other`` represents the same value as this instance; otherwise, ``False``.
        """
        if not isinstance(other, Color):
            return False
        return self.r == other.r and self.g == other.g and self.b == other.b and self.a == other.a

    def __copy__(self) -> Color:
        """Return a shallow copy of the instance.

        Returns:
            Shallow copy of the instance.
        """
        return type(self)(self.r, self.g, self.b, self.a)

    def __str__(self) -> str:
        """Return a human-readable representation of the instance.

        Returns:
            Human-readable representation of the instance.
        """
        return f"({self.r}, {self.g}, {self.b}, {self.a})"

    def __repr__(self) -> str:
        """Return a developer-oriented representation of the instance.

        Returns:
            Developer-oriented representation of the instance.
        """
        return f"Color(r={self.r}, g={self.g}, b={self.b}, a={self.a})"


class Coord:
    """Represents an integer point in viewport coordinates.

    Attributes:
        x: Horizontal coordinate.
        y: Vertical coordinate.
    """

    __slots__ = "x", "y"

    x: Final[int]
    y: Final[int]

    def __init__(self, x: int, y: int) -> None:
        """Initialize the coord with its initial configuration.

        Args:
            x: Horizontal coordinate or component.
            y: Vertical coordinate or component.
        """
        self.x = x
        self.y = y

    def __eq__(self, other: object) -> bool:
        """Return whether ``other`` represents the same value as this instance.

        Args:
            other: Object to compare against this instance.

        Returns:
            ``True`` when ``other`` represents the same value as this instance; otherwise, ``False``.
        """
        if not isinstance(other, Coord):
            return False
        return self.x == other.x and self.y == other.y

    def __str__(self) -> str:
        """Return a human-readable representation of the instance.

        Returns:
            Human-readable representation of the instance.
        """
        return f"{self.x},{self.y}"

    def __repr__(self) -> str:
        """Return a developer-oriented representation of the instance.

        Returns:
            Developer-oriented representation of the instance.
        """
        return f"Coord(x={self.x}, y={self.y})"


class Rect:
    """Represents an integer rectangle.

    Attributes:
        x: Horizontal coordinate.
        y: Vertical coordinate.
        width: Width in pixels.
        height: Height in pixels.
        left: Left edge coordinate.
        top: Top edge coordinate.
        right: Right edge coordinate.
        bottom: Bottom edge coordinate.
        x_center: Horizontal center coordinate.
        y_center: Vertical center coordinate.
        center: Center coordinate.
    """

    __slots__ = "x", "y", "width", "height", "left", "top", "right", "bottom", "x_center", "y_center", "center"

    x: Final[int]
    y: Final[int]

    width: Final[int]
    height: Final[int]

    left: Final[int]
    top: Final[int]
    right: Final[int]
    bottom: Final[int]

    x_center: Final[int]
    y_center: Final[int]

    center: Final[Coord]

    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        """Initialize the rect with its initial configuration.

        Args:
            x: Horizontal coordinate or component.
            y: Vertical coordinate or component.
            width: Width value used for sizing.
            height: Height value used for sizing.
        """
        self.x = x
        self.y = y

        if width < 0:
            raise ValueError("Width must be non-negative")
        if height < 0:
            raise ValueError("Height must be non-negative")

        self.width = width
        self.height = height

        self.left = x
        self.top = y
        self.right = x + width
        self.bottom = y + height

        self.x_center = x + width // 2
        self.y_center = y + self.height // 2

        self.center = Coord(self.x_center, self.y_center)

    def scale(self, factor: float) -> Rect:
        """Return a new coordinate scaled by the given factors.

        Args:
            factor: Numeric factor to validate.

        Returns:
            A scaled copy of the coordinate.
        """
        if factor < 0:
            raise ValueError("Scale factor must be non-negative")

        new_width = int(self.width * factor)
        new_height = int(self.height * factor)
        return Rect(
            x=self.x + (self.width - new_width) // 2,
            y=self.y + (self.height - new_height) // 2,
            width=new_width,
            height=new_height,
        )

    def with_xy(self, x: int, y: int) -> Rect:
        """Return a copy with updated x and y coordinates.

        Args:
            x: Horizontal coordinate to use.
            y: Vertical coordinate to use.

        Returns:
            A copy with replaced x and y coordinates.
        """
        return Rect(x=x, y=y, width=self.width, height=self.height)

    def __eq__(self, other: object) -> bool:
        """Return whether ``other`` represents the same value as this instance.

        Args:
            other: Object to compare against this instance.

        Returns:
            ``True`` when ``other`` represents the same value as this instance; otherwise, ``False``.
        """
        if not isinstance(other, Rect):
            return False
        return self.x == other.x and self.y == other.y and self.width == other.width and self.height == other.height

    def __copy__(self) -> Rect:
        """Return a shallow copy of the instance.

        Returns:
            Shallow copy of the instance.
        """
        return type(self)(x=self.x, y=self.y, width=self.width, height=self.height)

    def __str__(self) -> str:
        """Return a human-readable representation of the instance.

        Returns:
            Human-readable representation of the instance.
        """
        return f"Rect(x={self.x}, y={self.y}, width={self.width}, height={self.height})"

    __repr__ = __str__


NULL_RECT = Rect(0, 0, 0, 0)
"""Zero-sized rectangle used as a reusable empty layout placeholder."""


class Viewport:
    """Represents the render target viewport.

    Attributes:
        x: Horizontal coordinate.
        y: Vertical coordinate.
        width: Width in pixels.
        height: Height in pixels.
    """

    __slots__ = "x", "y", "width", "height"

    x: Final[int]
    y: Final[int]
    width: Final[int]
    height: Final[int]

    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        """Initialize the viewport with its initial configuration.

        Args:
            x: Horizontal coordinate or component.
            y: Vertical coordinate or component.
            width: Width value used for sizing.
            height: Height value used for sizing.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @property
    def left(self) -> int:
        """Left edge coordinate.

        Returns:
            Left edge coordinate.
        """
        return self.x

    @property
    def top(self) -> int:
        """Top edge coordinate.

        Returns:
            Top edge coordinate.
        """
        return self.y

    @property
    def right(self) -> int:
        """Right edge coordinate.

        Returns:
            Right edge coordinate.
        """
        return self.x + self.width

    @property
    def bottom(self) -> int:
        """Bottom edge coordinate.

        Returns:
            Bottom edge coordinate.
        """
        return self.y + self.height

    def as_rect(self) -> Rect:
        """Return the coordinate pair as a rectangle object.

        Returns:
            Rectangle representation of the coordinate pair.
        """
        return Rect(self.x, self.y, self.width, self.height)

    def __eq__(self, other: object) -> bool:
        """Return whether ``other`` represents the same value as this instance.

        Args:
            other: Object to compare against this instance.

        Returns:
            ``True`` when ``other`` represents the same value as this instance; otherwise, ``False``.
        """
        if not isinstance(other, Viewport):
            return False
        return self.x == other.x and self.y == other.y and self.width == other.width and self.height == other.height

    def __str__(self) -> str:
        """Return a human-readable representation of the instance.

        Returns:
            Human-readable representation of the instance.
        """
        return f"Viewport(x={self.x}, y={self.y}, width={self.width}, height={self.height})"

    __repr__ = __str__


__all__ = [
    "Arrow",
    "Color",
    "ColorMapping",
    "Coord",
    "HorizontalAlign",
    "NULL_RECT",
    "Rect",
    "VerticalAlign",
    "Viewport",
]
