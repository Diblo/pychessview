# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Controller protocols for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ...core.query.board_query import BoardQuery
    from ...core.session.protocols import (
        AnnotationSessionProtocol,
        GameSessionProtocol,
        InteractionSessionProtocol,
        PromotionSessionProtocol,
    )
    from ...core.state.view_state import ViewState
    from ...layout.primitives import Coord
    from ..controller_event_result import ControllerEventResult
    from ..input.modifiers import Modifier
    from ..input.mouse_buttons import MouseButton


class ControllerProtocol(Protocol):
    """Protocol for controllers that handle board interaction."""

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
    ) -> ControllerProtocol:
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
        ...

    def on_press(self, coord: Coord, button: MouseButton, modifier: Modifier | None = None) -> ControllerEventResult:
        """Handle the press event.

        Args:
            coord: Pointer position in viewport coordinates.
            button: Mouse button that triggered the event.
            modifier: Optional keyboard modifier.

        Returns:
            ControllerEventResult describing whether the press initiated or
            contributed to an active interaction step (e.g. piece selection,
            drag start, or annotation start) and whether the view should be
            redrawn.
        """
        ...

    def on_press_outside_view(self) -> ControllerEventResult:
        """Handle the press outside view event.

        Returns:
            ControllerEventResult describing any required visual cleanup or
            redraw. Outside-view handlers do not perform interaction steps and
            therefore return handled=False.
        """
        ...

    def on_pointer_move(self, coord: Coord, modifier: Modifier | None = None) -> ControllerEventResult:
        """Handle the pointer move event.

        Args:
            coord: Pointer position in viewport coordinates.
            modifier: Optional keyboard modifier.

        Returns:
            ControllerEventResult describing whether the move contributed to an
            active interaction step (e.g. drag update or annotation preview)
            and whether the view should be redrawn.
        """
        ...

    def on_pointer_move_outside_view(self) -> ControllerEventResult:
        """Handle the pointer move outside view event.

        Returns:
            ControllerEventResult describing any required visual cleanup or
            redraw. Outside-view handlers do not perform interaction steps and
            therefore return handled=False.
        """
        ...

    def on_release(self, coord: Coord, button: MouseButton, modifier: Modifier | None = None) -> ControllerEventResult:
        """Handle the release event.

        Args:
            coord: Pointer position in viewport coordinates.
            button: Mouse button that triggered the event.
            modifier: Optional keyboard modifier.

        Returns:
            ControllerEventResult describing whether the release completed or
            modified an active interaction step (e.g. move execution,
            annotation commit, or promotion handling) and whether the view
            should be redrawn.
        """
        ...

    def on_release_outside_view(self) -> ControllerEventResult:
        """Handle the release outside view event.

        Returns:
            ControllerEventResult describing any required visual cleanup or
            redraw. Outside-view handlers do not perform interaction steps and
            therefore return handled=False.
        """
        ...
