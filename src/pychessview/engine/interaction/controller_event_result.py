# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Result object for controller pointer-event handling."""

from typing import Any


class ControllerEventResult:
    """Result of controller pointer-event handling.

    This result describes the outcome of processing a pointer event in the
    interaction layer. It is independent of any GUI framework.

    Attributes:
        handled: True if the pointer event occurred inside the board view.
            Outside-view cleanup paths return False.

        requires_render: True if the interaction changed visual state and the
            view should be redrawn.
    """

    __slots__ = "_handled", "_requires_render"

    _handled: bool
    _requires_render: bool

    def __init__(self, *, handled: bool = False, requires_render: bool = False) -> None:
        """Initialize the controller event result.

        Args:
            handled: True if the pointer event occurred inside the board view.
            requires_render: True if the interaction changed visual state and the
                view should be redrawn.
        """
        object.__setattr__(self, "_handled", handled)
        object.__setattr__(self, "_requires_render", requires_render)

    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent mutation after initialization."""
        if hasattr(self, name):
            raise AttributeError(f"{self.__class__.__name__} is immutable")
        object.__setattr__(self, name, value)

    @property
    def handled(self) -> bool:
        """Return whether the pointer event occurred inside the board view."""
        return self._handled

    @property
    def requires_render(self) -> bool:
        """Return whether the interaction requires the view to be redrawn."""
        return self._requires_render

    def __repr__(self) -> str:
        """Return a developer-oriented representation of the instance."""
        return f"{self.__class__.__name__}(handled={self._handled}, requires_render={self._requires_render})"

    def __eq__(self, other: object) -> bool:
        """Return whether two results are equal."""
        if not isinstance(other, ControllerEventResult):
            return NotImplemented
        return self._handled == other._handled and self._requires_render == other._requires_render

    def __hash__(self) -> int:
        """Return a hash value for the instance."""
        return hash((self._handled, self._requires_render))
