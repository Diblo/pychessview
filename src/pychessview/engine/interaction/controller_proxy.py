# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Proxy wrapper for controllers in the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .controller.null_controller import NullController
from .controller.protocols import ControllerProtocol

if TYPE_CHECKING:
    from ..core.query.board_query import BoardQuery
    from ..core.session.protocols import (
        AnnotationSessionProtocol,
        GameSessionProtocol,
        InteractionSessionProtocol,
        PromotionSessionProtocol,
    )
    from ..core.state.view_state import ViewState
    from ..layout.primitives import Coord
    from .controller_event_result import ControllerEventResult
    from .input.modifiers import Modifier
    from .input.mouse_buttons import MouseButton


class ControllerProxy(ControllerProtocol):
    """Proxy that allows the active controller to be swapped."""

    __slots__ = "_impl"

    _impl: ControllerProtocol

    def __init__(self, impl: ControllerProtocol) -> None:
        """Initialize the proxy with the controller implementation to delegate interaction calls to.

        Args:
            impl: Value used to initialize ``impl``.
        """
        self._impl = impl

    @classmethod
    def create(
        cls,
        *,
        view_state: ViewState,
        game: GameSessionProtocol,
        interaction: InteractionSessionProtocol,
        annotation: AnnotationSessionProtocol,
        promotion: PromotionSessionProtocol,
        query: BoardQuery,
    ) -> ControllerProxy:
        """Create an instance from the provided collaborators.

        Args:
            view_state: View state to use.
            game: Game session that exposes board-state operations.
            interaction: Interaction session that manages selection and drag state.
            annotation: Annotation session that manages circles and arrows.
            promotion: Promotion session that manages promotion choice flow.
            query: Board query helper to use.

        Returns:
            A newly created instance of ``cls``.
        """
        return cls(
            NullController.create(
                view_state=view_state,
                game=game,
                interaction=interaction,
                annotation=annotation,
                promotion=promotion,
                query=query,
            )
        )

    def switch_controller(self, impl: ControllerProtocol) -> None:
        """Switch the active controller.

        Args:
            impl: Implementation instance to delegate to.
        """
        self._impl = impl

    def on_press(self, coord: Coord, button: MouseButton, modifier: Modifier | None = None) -> ControllerEventResult:
        """Handle the press event.

        Args:
            coord: Pointer position in viewport coordinates.
            button: Mouse button that triggered the event.
            modifier: Optional keyboard modifier.

        Returns:
            Event result returned by the active controller implementation.
        """
        return self._impl.on_press(coord, button, modifier)

    def on_press_outside_view(self) -> ControllerEventResult:
        """Handle the press outside view event.

        Returns:
            Event result returned by the active controller implementation.
        """
        return self._impl.on_press_outside_view()

    def on_pointer_move(self, coord: Coord, modifier: Modifier | None = None) -> ControllerEventResult:
        """Handle the pointer move event.

        Args:
            coord: Pointer position in viewport coordinates.
            modifier: Optional keyboard modifier.

        Returns:
            Event result returned by the active controller implementation.
        """
        return self._impl.on_pointer_move(coord, modifier)

    def on_pointer_move_outside_view(self) -> ControllerEventResult:
        """Handle the pointer move outside view event.

        Returns:
            Event result returned by the active controller implementation.
        """
        return self._impl.on_pointer_move_outside_view()

    def on_release(self, coord: Coord, button: MouseButton, modifier: Modifier | None = None) -> ControllerEventResult:
        """Handle the release event.

        Args:
            coord: Pointer position in viewport coordinates.
            button: Mouse button that triggered the event.
            modifier: Optional keyboard modifier.

        Returns:
            Event result returned by the active controller implementation.
        """
        return self._impl.on_release(coord, button, modifier)

    def on_release_outside_view(self) -> ControllerEventResult:
        """Handle the release outside view event.

        Returns:
            Event result returned by the active controller implementation.
        """
        return self._impl.on_release_outside_view()
