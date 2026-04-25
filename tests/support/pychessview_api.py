# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Support API for pychessview integration tests."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TypeVar

import pytest

SRC_DIR = str(Path(__file__).resolve().parents[2] / "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

pytest.importorskip("chess")

from pychessview import StandardChessFactory, View  # noqa: E402
from pychessview.engine.core.domain.game_spec import GameSpec  # noqa: E402
from pychessview.engine.core.primitives import Square  # noqa: E402
from pychessview.engine.interaction.input import Modifier, MouseButton  # noqa: E402
from pychessview.engine.layout.primitives import Coord  # noqa: E402
from pychessview.engine.render.renderer.null_renderer import (  # noqa: E402
    DrawArrowCommand,
    DrawCircleCommand,
    DrawTextInkCommand,
    NullRenderer,
    RenderCommand,
)

STANDARD_START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
"""Default standard chess position used by integration tests."""

E2_E4_PLACEMENT = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR"
"""Expected piece placement after the standard opening move e2-e4."""

PROMOTION_READY_FEN = "4k3/P7/8/8/8/8/8/4K3 w - - 0 1"
"""Legal position where white can promote with a7-a8."""

PROMOTED_QUEEN_PLACEMENT = "Q3k3/8/8/8/8/8/8/4K3"
"""Expected piece placement after promoting the a-pawn to a queen."""

KINGS_ONLY_FEN = "8/8/8/8/8/8/8/K6k w - - 0 1"
"""Minimal legal position used for load and reset flow tests."""

BLACK_TO_MOVE_KINGS_ONLY_FEN = "8/8/8/8/8/8/8/K6k b - - 0 1"
"""Minimal legal position with black to move used for explicit reset tests."""

TCommand = TypeVar("TCommand", bound=RenderCommand)


@dataclass(slots=True)
class ChessboardHarness:
    """Test harness that exposes the public pychessview view and renderer output.

    Attributes:
        view: Public view under test.
        renderer: Null renderer used to observe frame output.
        width: Viewport width used for pointer mapping and rendering.
        height: Viewport height used for pointer mapping and rendering.
    """

    view: View
    renderer: NullRenderer
    width: int
    height: int

    def render(self) -> tuple[RenderCommand, ...]:
        """Render one frame and return the commands produced for that frame.

        Returns:
            Commands recorded by the null renderer for the latest frame only.
        """
        self.renderer.commands.clear()
        self.view.render_frame(self.width, self.height)
        return tuple(self.renderer.commands)

    def coord_for_square(self, square: Square) -> Coord:
        """Return a stable viewport coordinate inside the requested square.

        Args:
            square: Board square to locate in the current rendered layout.

        Returns:
            A coordinate near the center of the rendered square.

        Raises:
            AssertionError: If the square is not present in the current layout.
        """
        self.render()
        min_x: int | None = None
        max_x: int | None = None
        min_y: int | None = None
        max_y: int | None = None

        for y in range(0, self.height, 4):
            for x in range(0, self.width, 4):
                if self.view.query.square_at(x, y) != square:
                    continue
                min_x = x if min_x is None else min(min_x, x)
                max_x = x if max_x is None else max(max_x, x)
                min_y = y if min_y is None else min(min_y, y)
                max_y = y if max_y is None else max(max_y, y)

        if min_x is None or max_x is None or min_y is None or max_y is None:
            raise AssertionError(f"square is not visible in the current layout: {square!r}")

        return Coord((min_x + max_x) // 2, (min_y + max_y) // 2)

    def coord_for_promotion_index(self, index: int) -> Coord:
        """Return a viewport coordinate inside the requested promotion option.

        Args:
            index: Zero-based promotion option index to locate.

        Returns:
            A coordinate that resolves to the requested promotion option.

        Raises:
            AssertionError: If the promotion option is not visible.
        """
        self.render()
        min_x: int | None = None
        max_x: int | None = None
        min_y: int | None = None
        max_y: int | None = None

        for y in range(0, self.height, 4):
            for x in range(0, self.width, 4):
                if self.view.query.promotion_index_at(x, y) != index:
                    continue
                min_x = x if min_x is None else min(min_x, x)
                max_x = x if max_x is None else max(max_x, x)
                min_y = y if min_y is None else min(min_y, y)
                max_y = y if max_y is None else max(max_y, y)

        if min_x is None or max_x is None or min_y is None or max_y is None:
            raise AssertionError(f"promotion option is not visible in the current layout: {index}")

        return Coord((min_x + max_x) // 2, (min_y + max_y) // 2)


def create_standard_game_spec(default_fen: str | None = None) -> GameSpec:
    """Create the standard chess game specification used by integration tests.

    Args:
        default_fen: Optional default FEN for the created game specification.

    Returns:
        Standard chess game specification.
    """
    return StandardChessFactory.create_game_spec(default_fen)


def board_square(file_name: str, rank: int) -> Square:
    """Return a board square from algebraic-style file and rank values.

    Args:
        file_name: Single-letter file name from ``a`` through ``h``.
        rank: One-based board rank.

    Returns:
        Square matching the requested file and rank.
    """
    return Square(ord(file_name.lower()) - ord("a"), rank - 1)


def create_standard_harness(
    *,
    width: int = 640,
    height: int = 640,
    default_fen: str | None = None,
) -> ChessboardHarness:
    """Create a fully wired standard chess view with an observable renderer.

    Args:
        width: Viewport width used by the test harness.
        height: Viewport height used by the test harness.
        default_fen: Optional default FEN for the standard chess view.

    Returns:
        Harness around a real ``View`` and ``NullRenderer``.
    """
    renderer = NullRenderer()
    view = View(renderer, create_standard_game_spec(default_fen), width=width, height=height)
    return ChessboardHarness(view=view, renderer=renderer, width=width, height=height)


def piece_placement(fen: str) -> str:
    """Return only the piece-placement field from a FEN string.

    Args:
        fen: FEN string to inspect.

    Returns:
        First FEN field containing only piece placement.
    """
    return fen.split()[0]


def command_count(commands: tuple[RenderCommand, ...], command_type: type[TCommand]) -> int:
    """Return how many commands match the requested command type.

    Args:
        commands: Render commands to inspect.
        command_type: Concrete command type to count.

    Returns:
        Number of commands of the requested type.
    """
    return sum(isinstance(command, command_type) for command in commands)


def rendered_circle_count(harness: ChessboardHarness) -> int:
    """Return the number of circle annotation draw commands in the latest frame.

    Args:
        harness: Harness whose renderer should be inspected.

    Returns:
        Number of rendered circle commands.
    """
    return command_count(harness.render(), DrawCircleCommand)


def rendered_arrow_count(harness: ChessboardHarness) -> int:
    """Return the number of arrow annotation draw commands in the latest frame.

    Args:
        harness: Harness whose renderer should be inspected.

    Returns:
        Number of rendered arrow commands.
    """
    return command_count(harness.render(), DrawArrowCommand)


def rendered_label_texts(harness: ChessboardHarness) -> tuple[str, ...]:
    """Return label texts rendered by the latest frame.

    Args:
        harness: Harness whose renderer should be inspected.

    Returns:
        Text values from rendered label commands.
    """
    commands = harness.render()
    return tuple(command.item.text for command in commands if isinstance(command, DrawTextInkCommand))


def press_square(
    harness: ChessboardHarness,
    square: Square,
    *,
    button: MouseButton = MouseButton.LEFT,
    modifier: Modifier | None = None,
) -> None:
    """Send a controller press to a rendered square.

    Args:
        harness: Harness whose controller should receive the event.
        square: Board square to press.
        button: Mouse button to send.
        modifier: Optional keyboard modifier to send.
    """
    harness.view.controller.on_press(harness.coord_for_square(square), button, modifier)


def move_pointer_to_square(harness: ChessboardHarness, square: Square, modifier: Modifier | None = None) -> None:
    """Send a controller pointer move to a rendered square.

    Args:
        harness: Harness whose controller should receive the event.
        square: Board square to move over.
        modifier: Optional keyboard modifier to send.
    """
    harness.view.controller.on_pointer_move(harness.coord_for_square(square), modifier)


def release_square(
    harness: ChessboardHarness,
    square: Square,
    *,
    button: MouseButton = MouseButton.LEFT,
    modifier: Modifier | None = None,
) -> None:
    """Send a controller release to a rendered square.

    Args:
        harness: Harness whose controller should receive the event.
        square: Board square to release over.
        button: Mouse button to send.
        modifier: Optional keyboard modifier to send.
    """
    harness.view.controller.on_release(harness.coord_for_square(square), button, modifier)


def drag_piece(harness: ChessboardHarness, from_square: Square, to_square: Square) -> None:
    """Drag a piece from one square to another through the public controller.

    Args:
        harness: Harness whose controller should receive the interaction.
        from_square: Square containing the piece to move.
        to_square: Destination square.
    """
    press_square(harness, from_square)
    move_pointer_to_square(harness, to_square)
    release_square(harness, to_square)


def create_circle_annotation(harness: ChessboardHarness, square: Square) -> None:
    """Create a primary circle annotation on a square through controller input.

    Args:
        harness: Harness whose controller should receive the interaction.
        square: Square that should receive the circle.
    """
    press_square(harness, square, modifier=Modifier.SHIFT)
    release_square(harness, square, modifier=Modifier.SHIFT)


def create_arrow_annotation(harness: ChessboardHarness, from_square: Square, to_square: Square) -> None:
    """Create a primary arrow annotation through controller drag input.

    Args:
        harness: Harness whose controller should receive the interaction.
        from_square: Arrow origin square.
        to_square: Arrow target square.
    """
    press_square(harness, from_square, modifier=Modifier.SHIFT)
    move_pointer_to_square(harness, to_square, Modifier.SHIFT)
    release_square(harness, to_square, modifier=Modifier.SHIFT)


def delete_circle_annotation(harness: ChessboardHarness, square: Square) -> None:
    """Delete a circle annotation through right-click controller input.

    Args:
        harness: Harness whose controller should receive the interaction.
        square: Square whose circle annotation should be removed.
    """
    press_square(harness, square, button=MouseButton.RIGHT)
    release_square(harness, square, button=MouseButton.RIGHT)


def delete_arrow_annotation(harness: ChessboardHarness, from_square: Square, to_square: Square) -> None:
    """Delete an arrow annotation through right-drag controller input.

    Args:
        harness: Harness whose controller should receive the interaction.
        from_square: Arrow origin square.
        to_square: Arrow target square.
    """
    press_square(harness, from_square, button=MouseButton.RIGHT)
    move_pointer_to_square(harness, to_square)
    release_square(harness, to_square, button=MouseButton.RIGHT)


def release_promotion_choice(harness: ChessboardHarness, index: int) -> None:
    """Release the controller over a promotion choice.

    Args:
        harness: Harness whose controller should receive the release.
        index: Promotion choice index to select.
    """
    harness.view.controller.on_release(harness.coord_for_promotion_index(index), MouseButton.LEFT)
