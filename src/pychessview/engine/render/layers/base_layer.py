# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Base rendering layer for the pychessview package."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from ...core.state.base import State
    from ...core.state.view_state import ViewState
    from ...layout.models.base import Layout
    from ..renderer.protocol import RendererProtocol


StateT = TypeVar("StateT", bound="State | None")
"""Type variable for the state handled by a rendering layer."""
LayoutT = TypeVar("LayoutT", bound="Layout")
"""Type variable for the layout handled by a rendering layer."""


class Layer(ABC, Generic[StateT, LayoutT]):
    """Base class for rendering layers.

    Attributes:
        view_state: View state used to build layout or render output.
        state: State object rendered by the layer.
        renderer: Renderer used by the layer or session.
        layout: Layout object used by the layer.
    """

    __slots__ = "view_state", "state", "layout", "renderer"

    view_state: ViewState
    state: StateT
    renderer: RendererProtocol
    layout: LayoutT

    def __init__(self, view_state: ViewState, state: StateT, renderer: RendererProtocol, layout: LayoutT) -> None:
        """Initialize the layer with its initial configuration.

        Args:
            view_state: View state used to control the rendered board presentation.
            state: State object used to initialize or synchronize the instance.
            renderer: Renderer instance used to turn render items into drawing commands.
            layout: Layout object used to describe board geometry or render placement.
        """
        self.view_state = view_state
        self.state = state
        self.renderer = renderer
        self.layout = layout

    @abstractmethod
    def render(self) -> None:
        """Render the layer using the active renderer and current layout state."""
        ...
