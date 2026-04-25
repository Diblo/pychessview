# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Base render item definitions for the pychessview package."""

from copy import copy
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self


class Item:
    """Base class for renderable items."""

    __slots__ = ()

    def copy(self) -> "Self":
        """Return a shallow copy of the item.

        Returns:
            A shallow copy of the item.
        """
        return copy(self)

    def __eq__(self, other: object) -> bool:
        """Return whether ``other`` represents the same value as this instance.

        Args:
            other: Object to compare against this instance.

        Returns:
            ``True`` when ``other`` represents the same value as this instance; otherwise, ``False``.
        """
        if type(self) is not type(other):
            return False

        slots = type(self).__slots__
        if isinstance(slots, str):
            slots = (slots,)

        return all(getattr(self, field) == getattr(other, field) for field in slots)

    def __str__(self) -> str:
        """Return a human-readable representation of the instance.

        Returns:
            Human-readable representation of the instance.
        """
        slots = type(self).__slots__
        if isinstance(slots, str):
            slots = (slots,)

        field_parts = ", ".join(f"{field}={getattr(self, field)!r}" for field in slots)
        return f"{type(self).__name__}({field_parts})"

    __repr__ = __str__
