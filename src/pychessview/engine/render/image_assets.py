# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Image asset value objects for the pychessview package."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final


class ImageAsset:
    """Stores an image path together with its dimensions.

    Attributes:
        path: Filesystem path to the asset.
        width: Width in pixels.
        height: Height in pixels.
    """

    __slots__ = "path", "width", "height"

    path: Final[Path]
    width: Final[int]
    height: Final[int]

    def __init__(self, path: str | Path, width: int, height: int) -> None:
        """Initialize the image asset with its initial configuration.

        Args:
            path: Value used to initialize ``path``.
            width: Width value used for sizing.
            height: Height value used for sizing.
        """
        self.path = Path(path)
        self.width = width
        self.height = height

    def __eq__(self, other: object) -> bool:
        """Return whether ``other`` represents the same value as this instance.

        Args:
            other: Object to compare against this instance.

        Returns:
            ``True`` when ``other`` represents the same value as this instance; otherwise, ``False``.
        """
        if not isinstance(other, ImageAsset):
            return False
        return self.path == other.path and self.width == other.width and self.height == other.height

    def __fspath__(self) -> str:
        """Return the filesystem path represented by the instance.

        Returns:
            Filesystem path represented by the instance.
        """
        return str(self.path)

    def __copy__(self) -> "ImageAsset":
        """Return a shallow copy of the instance.

        Returns:
            Shallow copy of the instance.
        """
        return type(self)(self.path.as_posix(), self.width, self.height)

    def __str__(self) -> str:
        """Return a human-readable representation of the instance.

        Returns:
            Human-readable representation of the instance.
        """
        return self.path.as_posix()

    def __repr__(self) -> str:
        """Return a developer-oriented representation of the instance.

        Returns:
            Developer-oriented representation of the instance.
        """
        return f"ImageAsset(path={self.path.as_posix()!r}, width={self.width}, height={self.height})"
