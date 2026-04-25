# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Null controller implementation for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..controller_event_result import ControllerEventResult
from .protocols import ControllerProtocol

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
    from ..input.modifiers import Modifier
    from ..input.mouse_buttons import MouseButton


class NullController(ControllerProtocol):
    """Controller that declines all interaction."""

    def __init__(
        self,
        *,
        view_state: ViewState,
        game: GameSessionProtocol,
        interaction: InteractionSessionProtocol,
        annotation: AnnotationSessionProtocol,
        promotion: PromotionSessionProtocol,
        query: BoardQuery,
    ) -> None:
        """Initialize the null controller used when no interactive controller is configured.

        Args:
            view_state: Value supplied for ``view_state``.
            game: Game session or adapter to use.
            interaction: Interaction session to use.
            annotation: Annotation session to use.
            promotion: Value supplied for ``promotion``.
            query: Value supplied for ``query``.
        """
        _ = view_state, game, interaction, annotation, promotion, query

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
    ) -> NullController:
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
            view_state=view_state,
            game=game,
            interaction=interaction,
            annotation=annotation,
            promotion=promotion,
            query=query,
        )

    def on_press(self, coord: Coord, button: MouseButton, modifier: Modifier | None = None) -> ControllerEventResult:
        """Handle the press event.

        Args:
            coord: Pointer position in viewport coordinates.
            button: Mouse button that triggered the event.
            modifier: Optional keyboard modifier.

        Returns:
            A controller event result describing whether the press contributed
            to an active interaction step and whether the view should be
            redrawn.
        """
        _ = coord, modifier, button
        return ControllerEventResult()

    def on_press_outside_view(self) -> ControllerEventResult:
        """Handle the press outside view event.

        Returns:
            A controller event result describing any required visual cleanup
            or redraw outside the board view.
        """
        return ControllerEventResult()

    def on_pointer_move(self, coord: Coord, modifier: Modifier | None = None) -> ControllerEventResult:
        """Handle the pointer move event.

        Args:
            coord: Pointer position in viewport coordinates.
            modifier: Optional keyboard modifier.

        Returns:
            A controller event result describing whether the move contributed
            to an active interaction step and whether the view should be
            redrawn.
        """
        _ = coord, modifier
        return ControllerEventResult()

    def on_pointer_move_outside_view(self) -> ControllerEventResult:
        """Handle the pointer move outside view event.

        Returns:
            A controller event result describing any required visual cleanup
            or redraw outside the board view.
        """
        return ControllerEventResult()

    def on_release(self, coord: Coord, button: MouseButton, modifier: Modifier | None = None) -> ControllerEventResult:
        """Handle the release event.

        Args:
            coord: Pointer position in viewport coordinates.
            button: Mouse button that triggered the event.
            modifier: Optional keyboard modifier.

        Returns:
            A controller event result describing whether the release completed
            or modified an active interaction step and whether the view should
            be redrawn.
        """
        _ = coord, modifier, button
        return ControllerEventResult()

    def on_release_outside_view(self) -> ControllerEventResult:
        """Handle the release outside view event.

        Returns:
            A controller event result describing any required visual cleanup
            or redraw outside the board view.
        """
        return ControllerEventResult()
