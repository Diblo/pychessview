# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Shared helpers for pychessview unit tests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import pytest

import pychessview.engine.view as view_module
from pychessview.engine.core.domain.adapters.null_game_adapter import NullGameAdapter
from pychessview.engine.core.domain.adapters.protocol import GameAdapterProtocol
from pychessview.engine.core.domain.game_spec import GameSpec
from pychessview.engine.core.highlight_types import HighlightPlayer, HintStyle
from pychessview.engine.core.primitives import File, Move, Piece, PieceKind, PlayerColor, Rank, Square, SquareData
from pychessview.engine.core.query.board_query import BoardQuery
from pychessview.engine.core.session.board_session_builder import BoardSessionComponents
from pychessview.engine.core.session.game_session import GameSession
from pychessview.engine.core.session.interaction_session import InteractionSession
from pychessview.engine.core.session.promotion_session import PromotionSession
from pychessview.engine.core.session.protocols import (
    AnnotationSessionProtocol,
    GameSessionProtocol,
    InteractionSessionProtocol,
    PromotionSessionProtocol,
)
from pychessview.engine.core.state.annotation_state import AnnotationState
from pychessview.engine.core.state.highlight_state import HighlightState
from pychessview.engine.core.state.piece_ui_state import PieceUiState
from pychessview.engine.core.state.promotion_state import PromotionState
from pychessview.engine.core.state.view_state import ViewState
from pychessview.engine.interaction.controller.standard_chess_controller import StandardChessController
from pychessview.engine.interaction.controller_event_result import ControllerEventResult
from pychessview.engine.interaction.input.modifiers import Modifier
from pychessview.engine.interaction.input.mouse_buttons import MouseButton
from pychessview.engine.layout.layout_engine import LayoutEngine
from pychessview.engine.layout.primitives import Color, Coord, Rect, Viewport
from pychessview.engine.render.image_assets import ImageAsset
from pychessview.engine.render.items.arrow_item import ArrowItem
from pychessview.engine.render.items.circle_item import CircleItem
from pychessview.engine.render.items.color_square_item import ColorSquareItem
from pychessview.engine.render.items.image_square_item import ImageSquareItem
from pychessview.engine.render.items.label_item import LabelItem
from pychessview.engine.render.renderer.null_renderer import DrawSquareImageCommand, NullRenderer
from pychessview.engine.render.renderer.protocol import RendererProtocol
from pychessview.engine.theme.theme import Theme
from pychessview.engine.view import View

if TYPE_CHECKING:
    from pychessview.engine.interaction.controller.protocols import ControllerProtocol
    from pychessview.engine.render.layers.annotation_layer import AnnotationLayer
    from pychessview.engine.render.layers.board_layer import BoardLayer
    from pychessview.engine.render.layers.highlight_layer import HighlightLayer
    from pychessview.engine.render.layers.piece_layer import PieceLayer
    from pychessview.engine.render.layers.promotion_layer import PromotionLayer


class MutableAdapter(NullGameAdapter):
    """Small adapter fake with explicit mutable piece placement.

    Attributes:
        stored_pieces: Piece placement returned by ``pieces``.
    """

    def __init__(self) -> None:
        """Initialize the fake adapter with empty explicit piece storage."""
        super().__init__("")
        self.stored_pieces: dict[Square, Piece] = {}

    def pieces(self) -> dict[Square, Piece]:
        """Return the currently stored test piece placement.

        Returns:
            A copy of the configured test piece mapping.
        """
        return dict(self.stored_pieces)


class MinimalThemeStub:
    """Minimal theme stand-in exposing only the border factor used by layout."""

    def __init__(self, border_factor: float) -> None:
        """Store the border factor used by the layout engine."""
        self.border_factor = border_factor


def white_promotion_pieces() -> tuple[Piece, ...]:
    """Return the standard white promotion choices used by unit tests."""
    return (
        Piece(PlayerColor.WHITE, PieceKind.QUEEN),
        Piece(PlayerColor.WHITE, PieceKind.ROOK),
        Piece(PlayerColor.WHITE, PieceKind.BISHOP),
        Piece(PlayerColor.WHITE, PieceKind.KNIGHT),
    )


def black_promotion_pieces() -> tuple[Piece, ...]:
    """Return the standard black promotion choices used by unit tests."""
    return (
        Piece(PlayerColor.BLACK, PieceKind.QUEEN),
        Piece(PlayerColor.BLACK, PieceKind.ROOK),
        Piece(PlayerColor.BLACK, PieceKind.BISHOP),
        Piece(PlayerColor.BLACK, PieceKind.KNIGHT),
    )


def query_promotion_state() -> PromotionState:
    """Return promotion state with two white options for board-query tests."""
    return PromotionState(
        (
            Piece(PlayerColor.WHITE, PieceKind.QUEEN),
            Piece(PlayerColor.WHITE, PieceKind.ROOK),
        ),
        (),
    )


def create_board_query(
    view_state: ViewState | None = None, promotion_state: PromotionState | None = None
) -> BoardQuery:
    """Return a board query with deterministic 80 by 80 geometry."""
    view_state = view_state or ViewState(PlayerColor.WHITE, show_border=False, stretch_to_fit=True)
    geometry = LayoutEngine(view_state, cast("Theme", MinimalThemeStub(0.0)), Viewport(0, 0, 80, 80))
    return BoardQuery(view_state, promotion_state or query_promotion_state(), geometry)


def create_layout_engine(view_state: ViewState | None = None, viewport: Viewport | None = None) -> LayoutEngine:
    """Return a layout engine backed by a small theme stub."""
    return LayoutEngine(
        view_state or ViewState(PlayerColor.WHITE),
        cast("Theme", MinimalThemeStub(0.05)),
        viewport or Viewport(10, 20, 100, 120),
    )


class ViewRendererSpy:
    """Renderer fake that records frame boundaries."""

    def __init__(self) -> None:
        """Initialize the renderer with an empty call log."""
        self.calls: list[tuple[str, object]] = []

    def begin_frame(self, viewport: Viewport) -> None:
        """Record the viewport used to begin a render frame."""
        self.calls.append(("begin", viewport))

    def draw_square_color(self, item: object) -> None:
        """Ignore square color drawing because layer tests cover render items."""

    def draw_square_image(self, item: object) -> None:
        """Ignore square image drawing because layer tests cover render items."""

    def draw_text_ink(self, item: object) -> None:
        """Ignore text drawing because layer tests cover render items."""

    def draw_circle(self, item: object, color: object) -> None:
        """Ignore circle drawing because layer tests cover render items."""

    def draw_arrow(self, item: object, color: object, points: object) -> None:
        """Ignore arrow drawing because layer tests cover render items."""

    def end_frame(self) -> None:
        """Record that the frame was closed."""
        self.calls.append(("end", ()))


class ViewThemeSpy:
    """Theme fake that records in-place theme replacement calls."""

    def __init__(self) -> None:
        """Initialize the theme with an empty load log."""
        self.load_calls: list[object] = []

    def load(self, theme: object) -> None:
        """Record the replacement theme passed through ``View.theme``."""
        self.load_calls.append(theme)


class ViewGeometryStub:
    """Geometry fake that stores viewport updates and renderability."""

    def __init__(self) -> None:
        """Initialize the geometry with a renderable default viewport."""
        self.viewport = Viewport(1, 2, 100, 200)
        self.is_renderable = True
        self.updates: list[Viewport] = []

    def update(self, viewport: Viewport) -> None:
        """Record and apply the requested viewport update."""
        self.updates.append(viewport)
        self.viewport = viewport


class ViewLayerSpy:
    """Layer fake that appends its name when rendered."""

    def __init__(self, name: str, render_order: list[str]) -> None:
        """Initialize the layer with a shared render-order log."""
        self.name = name
        self._render_order = render_order

    def render(self) -> None:
        """Record that this layer rendered."""
        self._render_order.append(self.name)


class ViewGameSessionSpy:
    """Game-session fake that records FEN loading and reset calls."""

    def __init__(self) -> None:
        """Initialize the game session with a visible FEN value."""
        self.fen = "current fen"
        self.load_fen_calls: list[str] = []
        self.reset_calls: list[str | None] = []

    def load_fen(self, fen: str) -> None:
        """Record direct FEN loads made through the view facade."""
        self.load_fen_calls.append(fen)

    def reset(self, fen: str | None = None) -> None:
        """Record board reset requests made through the view facade."""
        self.reset_calls.append(fen)


class ViewBoardSessionStub:
    """Board-session fake exposing the properties that View delegates to."""

    instances: list[ViewBoardSessionStub] = []

    def __init__(self, components: object) -> None:
        """Initialize the fake session from builder output."""
        self.components = components
        self.renderer = ViewRendererSpy()
        self.theme = ViewThemeSpy()
        self.view_state = object()
        self.geometry = ViewGeometryStub()
        self.game_session = ViewGameSessionSpy()
        self.interaction_session = object()
        self.annotation_session = object()
        self.promotion_session = object()
        self.query = object()
        self.controller = object()
        self.controller_enabled = True
        self.render_order: list[str] = []
        self.board_layer = ViewLayerSpy("board", self.render_order)
        self.highlight_layer = ViewLayerSpy("highlight", self.render_order)
        self.piece_layer = ViewLayerSpy("piece", self.render_order)
        self.annotation_layer = ViewLayerSpy("annotation", self.render_order)
        self.promotion_layer = ViewLayerSpy("promotion", self.render_order)
        self.load_game_calls: list[tuple[object, dict[str, object]]] = []
        type(self).instances.append(self)

    def load_game(self, game_spec: object, **kwargs: object) -> None:
        """Record game-loading calls made through the view facade."""
        self.load_game_calls.append((game_spec, kwargs))


class ViewBoardSessionBuilderStub:
    """Builder fake that records constructor wiring inputs."""

    calls: list[tuple[object, object, Viewport, dict[str, object]]] = []

    @staticmethod
    def build(renderer: object, game_spec: object, viewport: Viewport, **kwargs: object) -> object:
        """Record the arguments used by ``View`` to build a board session."""
        ViewBoardSessionBuilderStub.calls.append((renderer, game_spec, viewport, kwargs))
        return {"components": viewport}


def install_fake_view_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    """Install fake board-session construction collaborators into the view module."""
    ViewBoardSessionStub.instances = []
    ViewBoardSessionBuilderStub.calls = []
    monkeypatch.setattr(view_module, "BoardSession", ViewBoardSessionStub)
    monkeypatch.setattr(view_module, "BoardSessionBuilder", ViewBoardSessionBuilderStub)


def create_fake_view(monkeypatch: pytest.MonkeyPatch) -> tuple[View, ViewRendererSpy, GameSpec, ViewBoardSessionStub]:
    """Create a view backed by fake board-session collaborators."""
    install_fake_view_runtime(monkeypatch)
    renderer = ViewRendererSpy()
    game_spec = cast(GameSpec, object())
    view = View(cast(RendererProtocol, renderer), game_spec, width=640, height=480, x=5, y=6)
    return view, renderer, game_spec, ViewBoardSessionStub.instances[0]


class SessionAdapterStub:
    """Configurable game adapter fake used by session unit tests.

    Attributes:
        default_fen: FEN returned when a reset uses the adapter default.
        fen: Mutable FEN string exposed by the fake adapter.
        turn: Active player color returned by the fake adapter.
        move_history: Moves recorded by the fake adapter.
        placement: Mutable board placement used by piece queries and moves.
        legal_moves: Non-promotion moves accepted by ``is_legal_move``.
        legal_promotions: Promotion moves accepted by ``is_legal_move``.
        applied_moves: Moves applied through ``move``.
        promotions: Promotion moves applied through ``move``.
        legal_hints: Legal hint destinations keyed by origin square.
        pseudo_hints: Pseudo-legal hint destinations keyed by origin square.
        check: Check flag returned by ``is_check``.
        checkmate: Checkmate flag returned by ``is_checkmate``.
        king_square: King square returned by ``king``.
        detect_promotion_by_rank: Whether back-rank destinations should be treated as promotion moves.
    """

    def __init__(self) -> None:
        """Initialize the adapter with empty board state and default rule results."""
        self.default_fen = "default fen"
        self.fen = "current fen"
        self.turn = PlayerColor.WHITE
        self.move_history: tuple[Move, ...] = ()
        self.placement: dict[Square, Piece] = {}
        self.legal_moves: list[Move] = []
        self.legal_promotions: list[Move] = []
        self.applied_moves: list[Move] = []
        self.promotions: list[Move] = []
        self.legal_hints: dict[Square, set[Square]] = {}
        self.pseudo_hints: dict[Square, set[Square]] = {}
        self.check = False
        self.checkmate = False
        self.king_square: Square | None = None
        self.detect_promotion_by_rank = False

    def pieces(self) -> dict[Square, Piece]:
        """Return a copy of the configured board placement."""
        return dict(self.placement)

    def piece_at(self, square: Square) -> Piece | None:
        """Return the configured piece for ``square``."""
        return self.placement.get(square)

    def set_piece(self, square: Square, piece: Piece | None) -> None:
        """Place or clear a piece in the fake board mapping."""
        if piece is None:
            self.placement.pop(square, None)
            return
        self.placement[square] = piece

    def king(self, color: PlayerColor) -> Square | None:
        """Return the configured king square."""
        return self.king_square

    def is_legal_move(self, move: Move) -> bool:
        """Return whether ``move`` has been marked legal for this test."""
        if move.promotion is None:
            return move in self.legal_moves
        return move in self.legal_promotions

    def is_promotion_move(self, move: Move) -> bool:
        """Return whether the move is configured as a promotion move."""
        return self.detect_promotion_by_rank and move.to_square.rank in {0, 7}

    def has_move_history(self) -> bool:
        """Return whether the fake has stored any move history."""
        return bool(self.move_history)

    def move(self, move: Move) -> None:
        """Apply a move to the fake board placement and record it."""
        self.applied_moves.append(move)
        if move.promotion is not None:
            self.promotions.append(move)
        piece = self.placement.pop(move.from_square, None)
        if piece is not None:
            if move.promotion is not None:
                piece = Piece(piece.color, move.promotion)
            self.placement[move.to_square] = piece
        self.move_history = (*self.move_history, move)

    def is_check(self) -> bool:
        """Return the configured check flag."""
        return self.check

    def is_checkmate(self) -> bool:
        """Return the configured checkmate flag."""
        return self.checkmate

    def get_legal_hints(self, square: Square) -> set[Square]:
        """Return configured legal hint destinations."""
        return set(self.legal_hints.get(square, set()))

    def get_pseudo_legal_hints(self, square: Square, color: PlayerColor) -> set[Square]:
        """Return configured pseudo-legal hint destinations."""
        return set(self.pseudo_hints.get(square, set()))


def create_game_session(
    adapter: SessionAdapterStub,
) -> tuple[GameSession, HighlightState, PieceUiState, AnnotationState, PromotionState]:
    """Create a game session with directly inspectable state collaborators."""
    highlight_state = HighlightState()
    piece_ui_state = PieceUiState(adapter)
    annotation_state = AnnotationState()
    promotion_state = PromotionState((), ())
    return (
        GameSession(adapter, highlight_state, piece_ui_state, annotation_state, promotion_state),
        highlight_state,
        piece_ui_state,
        annotation_state,
        promotion_state,
    )


def create_interaction_session(
    adapter: SessionAdapterStub, view_state: ViewState | None = None
) -> tuple[InteractionSession, HighlightState, PieceUiState, PromotionState, AnnotationState]:
    """Create an interaction session with directly inspectable state collaborators."""
    if view_state is None:
        view_state = ViewState(PlayerColor.WHITE)
    highlight_state = HighlightState()
    piece_ui_state = PieceUiState(adapter)
    promotion_state = PromotionState((), ())
    annotation_state = AnnotationState()
    return (
        InteractionSession(view_state, adapter, highlight_state, piece_ui_state, promotion_state, annotation_state),
        highlight_state,
        piece_ui_state,
        promotion_state,
        annotation_state,
    )


class PromotionQueryStub:
    """Query fake that maps pointer coordinates to one promotion index."""

    def __init__(self, index: int | None) -> None:
        """Initialize the query with the index returned for all coordinates."""
        self.index = index
        self.calls: list[tuple[int, int]] = []

    def promotion_index_at(self, x: int, y: int) -> int | None:
        """Return the configured promotion index and record the queried coordinate."""
        self.calls.append((x, y))
        return self.index


def create_promotion_session(
    adapter: SessionAdapterStub, query: PromotionQueryStub
) -> tuple[PromotionSession, HighlightState, PieceUiState, AnnotationState, PromotionState]:
    """Create a promotion session with directly inspectable state collaborators."""
    adapter.detect_promotion_by_rank = True
    white_options = (
        Piece(PlayerColor.WHITE, PieceKind.QUEEN),
        Piece(PlayerColor.WHITE, PieceKind.ROOK),
    )
    black_options = (Piece(PlayerColor.BLACK, PieceKind.QUEEN),)
    highlight_state = HighlightState()
    piece_ui_state = PieceUiState(adapter)
    annotation_state = AnnotationState()
    promotion_state = PromotionState(white_options, black_options)
    return (
        PromotionSession(
            adapter,
            cast(BoardQuery, query),
            highlight_state,
            piece_ui_state,
            annotation_state,
            promotion_state,
        ),
        highlight_state,
        piece_ui_state,
        annotation_state,
        promotion_state,
    )


class BoardSessionControllerSpy:
    """Controller fake that returns a distinct result for press events."""

    def __init__(self, label: str) -> None:
        """Initialize the controller with a result label."""
        self.label = label
        self.result = ControllerEventResult(handled=True, requires_render=label == "game")
        self.calls: list[tuple[str, tuple[Any, ...]]] = []

    @classmethod
    def create(cls, **_: object) -> BoardSessionControllerSpy:
        """Create a controller fake while ignoring BoardSession collaborators."""
        return cls("created")

    def on_press(self, coord: Coord, button: MouseButton, modifier: object = None) -> ControllerEventResult:
        """Record press calls and return the controller-specific result."""
        self.calls.append(("press", (coord, button, modifier)))
        return self.result

    def on_press_outside_view(self) -> ControllerEventResult:
        """Return a neutral cleanup result."""
        return ControllerEventResult()

    def on_pointer_move(self, coord: Coord, modifier: object = None) -> ControllerEventResult:
        """Return a neutral move result."""
        return ControllerEventResult()

    def on_pointer_move_outside_view(self) -> ControllerEventResult:
        """Return a neutral cleanup result."""
        return ControllerEventResult()

    def on_release(self, coord: Coord, button: MouseButton, modifier: object = None) -> ControllerEventResult:
        """Return a neutral release result."""
        return ControllerEventResult()

    def on_release_outside_view(self) -> ControllerEventResult:
        """Return a neutral cleanup result."""
        return ControllerEventResult()


class BoardSessionThemeSpy:
    """Theme fake that records replacement loads."""

    def __init__(self) -> None:
        """Initialize the theme spy with an empty load log."""
        self.load_calls: list[object] = []

    def load(self, theme: object) -> None:
        """Record theme replacement requests."""
        self.load_calls.append(theme)


class BoardSessionGameAdapterProxySpy:
    """Game-adapter proxy fake with switch and highlight-query behavior."""

    def __init__(self) -> None:
        """Initialize the adapter proxy with no move history and no check."""
        self.default_fen = "default"
        self.fen = "fen"
        self.turn = PlayerColor.WHITE
        self.move_history: tuple[Move, ...] = ()
        self.switched_adapters: list[object] = []
        self.check = False
        self.checkmate = False
        self.king_square: Square | None = None

    def switch_adapter(self, impl: object) -> None:
        """Record adapter replacements requested by BoardSession."""
        self.switched_adapters.append(impl)

    def pieces(self) -> dict[Square, Piece]:
        """Return empty placement because rendering is outside these tests."""
        return {}

    def piece_at(self, square: Square) -> Piece | None:
        """Return no pieces because piece queries are outside these tests."""
        return None

    def set_piece(self, square: Square, piece: Piece | None) -> None:
        """Ignore piece placement because BoardSession does not mutate pieces directly."""

    def king(self, color: PlayerColor) -> Square | None:
        """Return the configured king square."""
        return self.king_square

    def is_legal_move(self, move: Move) -> bool:
        """Return false because move legality is outside BoardSession orchestration."""
        return False

    def is_promotion_move(self, move: Move) -> bool:
        """Return false because promotion detection is outside BoardSession orchestration."""
        return False

    def has_move_history(self) -> bool:
        """Return whether configured move history is present."""
        return bool(self.move_history)

    def move(self, move: Move) -> None:
        """Ignore moves because BoardSession does not apply them directly."""

    def is_check(self) -> bool:
        """Return the configured check flag."""
        return self.check

    def is_checkmate(self) -> bool:
        """Return the configured checkmate flag."""
        return self.checkmate

    def get_legal_hints(self, square: Square) -> set[Square]:
        """Return no hints because hint generation is outside these tests."""
        return set()

    def get_pseudo_legal_hints(self, square: Square, color: PlayerColor) -> set[Square]:
        """Return no hints because hint generation is outside these tests."""
        return set()


class BoardSessionPromotionSessionSpy:
    """Promotion-session fake that records configured piece options."""

    def __init__(self) -> None:
        """Initialize the fake with empty option logs."""
        self.white_options: list[tuple[Piece, ...]] = []
        self.black_options: list[tuple[Piece, ...]] = []

    def set_white_promotion_pieces(self, white_promotion_pieces: tuple[Piece, ...]) -> None:
        """Record white promotion options applied during game loading."""
        self.white_options.append(white_promotion_pieces)

    def set_black_promotion_pieces(self, black_promotion_pieces: tuple[Piece, ...]) -> None:
        """Record black promotion options applied during game loading."""
        self.black_options.append(black_promotion_pieces)


class ThemeProviderSpy:
    """Theme provider fake that returns one replacement theme."""

    def __init__(self, theme: object) -> None:
        """Initialize the provider with the theme to return."""
        self.theme = theme

    def create_theme(self) -> object:
        """Return the configured theme object."""
        return self.theme


class AdapterFactorySpy:
    """Adapter factory fake that records requested default FEN values."""

    def __init__(self, adapter: object) -> None:
        """Initialize the factory with the adapter to return."""
        self.adapter = adapter
        self.default_fen_calls: list[str | None] = []

    @classmethod
    def create(cls, default_fen: str) -> AdapterFactorySpy:
        """Create a factory with a placeholder adapter for protocol compatibility."""
        return cls(object())

    def create_game_adapter(self, default_fen: str | None = None) -> object:
        """Record the default FEN and return the configured replacement adapter."""
        self.default_fen_calls.append(default_fen)
        return self.adapter


class ControllerFactorySpy:
    """Controller factory fake that records collaborators passed by BoardSession."""

    def __init__(self, controller: BoardSessionControllerSpy) -> None:
        """Initialize the factory with the controller to return."""
        self.controller = controller
        self.calls: list[tuple[object, object, object, object, object, object]] = []

    def create_controller(
        self,
        view_state: object,
        game: object,
        interaction: object,
        annotation: object,
        promotion: object,
        query: object,
    ) -> BoardSessionControllerSpy:
        """Record collaborator wiring and return the configured controller."""
        self.calls.append((view_state, game, interaction, annotation, promotion, query))
        return self.controller


def build_board_session_components() -> tuple[
    BoardSessionComponents,
    BoardSessionGameAdapterProxySpy,
    BoardSessionThemeSpy,
    BoardSessionPromotionSessionSpy,
]:
    """Build fake BoardSession components with directly inspectable collaborators."""
    game_adapter = BoardSessionGameAdapterProxySpy()
    theme = BoardSessionThemeSpy()
    highlight_state = HighlightState()
    piece_ui_state = PieceUiState(cast(GameAdapterProtocol, game_adapter))
    annotation_state = AnnotationState()
    promotion_state = PromotionState((), ())
    promotion_session = BoardSessionPromotionSessionSpy()
    return (
        BoardSessionComponents(
            renderer=cast("RendererProtocol", object()),
            theme=cast("Theme", theme),
            view_state=ViewState(PlayerColor.WHITE),
            geometry=cast(Any, object()),
            game_adapter=cast(Any, game_adapter),
            highlight_state=highlight_state,
            piece_ui_state=piece_ui_state,
            annotation_state=annotation_state,
            promotion_state=promotion_state,
            game_session=cast("GameSessionProtocol", object()),
            interaction_session=cast("InteractionSessionProtocol", object()),
            annotation_session=cast("AnnotationSessionProtocol", object()),
            promotion_session=cast("PromotionSessionProtocol", promotion_session),
            query=cast("BoardQuery", object()),
            null_controller=cast("ControllerProtocol", BoardSessionControllerSpy("null")),
            game_controller=cast("ControllerProtocol", BoardSessionControllerSpy("game")),
            board_layer=cast("BoardLayer", object()),
            highlight_layer=cast("HighlightLayer", object()),
            piece_layer=cast("PieceLayer", object()),
            annotation_layer=cast("AnnotationLayer", object()),
            promotion_layer=cast("PromotionLayer", object()),
        ),
        game_adapter,
        theme,
        promotion_session,
    )


LAYER_RECT = Rect(1, 2, 10, 10)
"""Shared rectangle used for fake render items."""


def layer_image_item(name: str) -> ImageSquareItem:
    """Create an image item with an identifiable asset name."""
    return ImageSquareItem(ImageAsset(name, 1, 1), LAYER_RECT)


class BoardLayoutSpy:
    """Provide board layout items without constructing a full layout engine."""

    def __init__(self) -> None:
        """Initialize board layout call tracking."""
        self.update_calls = 0

    def update(self) -> None:
        """Record that the layer refreshed layout data."""
        self.update_calls += 1

    def background_item(self) -> ColorSquareItem:
        """Return the fake board background item."""
        return ColorSquareItem(Color(1, 1, 1), LAYER_RECT)

    def board_item(self) -> ColorSquareItem:
        """Return the fake board surface item."""
        return ColorSquareItem(Color(2, 2, 2), LAYER_RECT)

    def square_item(self, square: Square) -> ImageSquareItem:
        """Return the fake square texture item for ``square``."""
        return layer_image_item(f"square:{square.file.text}{square.rank.text}")

    def label_item(self, side: object, axis: object) -> LabelItem:
        """Return a label item that exposes the requested side and axis."""
        return LabelItem(LAYER_RECT, f"label:{side}:{axis}")


class AnnotationLayoutSpy:
    """Provide annotation layout items and record requested annotation payloads."""

    def __init__(self) -> None:
        """Initialize annotation layout call tracking."""
        self.update_calls = 0
        self.arrow_calls: list[tuple[object, Square, Square, bool]] = []
        self.circle_calls: list[tuple[object, Square]] = []

    def update(self) -> None:
        """Record that the layer refreshed layout data."""
        self.update_calls += 1

    def arrow(
        self, arrow_type: object, from_square: Square, to_square: Square, has_corner: bool = False
    ) -> tuple[ArrowItem, Color, tuple[Coord, Coord]]:
        """Return an arrow command payload for the requested annotation."""
        self.arrow_calls.append((arrow_type, from_square, to_square, has_corner))
        return ArrowItem(1, 2, 3), Color(len(self.arrow_calls), 0, 0), (Coord(1, 1), Coord(2, 2))

    def circle(self, circle_type: object, square: Square) -> tuple[CircleItem, Color]:
        """Return a circle command payload for the requested annotation."""
        self.circle_calls.append((circle_type, square))
        return CircleItem(4, LAYER_RECT), Color(0, len(self.circle_calls), 0)


class HighlightLayoutSpy:
    """Provide highlight image items without a full highlight layout."""

    def __init__(self) -> None:
        """Initialize highlight layout call tracking."""
        self.update_calls = 0

    def update(self) -> None:
        """Record that the layer refreshed layout data."""
        self.update_calls += 1

    def last_move(self, square: Square) -> ImageSquareItem:
        """Return a last-move image item for ``square``."""
        return layer_image_item(f"last:{square.file.text}{square.rank.text}")

    def check(self, square: Square) -> ImageSquareItem:
        """Return a check image item for ``square``."""
        return layer_image_item(f"check:{square.file.text}{square.rank.text}")

    def hint(self, player: HighlightPlayer, style: HintStyle, square: Square) -> ImageSquareItem:
        """Return a hint image item for ``player``, ``style``, and ``square``."""
        return layer_image_item(f"hint:{player.value}:{style.value}:{square.file.text}{square.rank.text}")

    def selected(self, player: HighlightPlayer, square: Square) -> ImageSquareItem:
        """Return a selected-square image item for ``player`` and ``square``."""
        return layer_image_item(f"selected:{player.value}:{square.file.text}{square.rank.text}")


class PieceStateStub:
    """Expose only the piece UI state used by ``PieceLayer``."""

    def __init__(self) -> None:
        """Initialize piece state with one normal and one dragged piece."""
        self.dragged_square = Square(File.E, Rank.TWO)
        self.dragged_position = Coord(90, 90)
        self.preview_move: Move | None = None
        self._pieces = {
            Square(File.A, Rank.ONE): Piece(PlayerColor.WHITE, PieceKind.KING),
            self.dragged_square: Piece(PlayerColor.WHITE, PieceKind.PAWN),
        }

    def pieces(self) -> dict[Square, Piece]:
        """Return the configured fake piece placement."""
        return dict(self._pieces)


class PieceLayoutSpy:
    """Provide piece render items without constructing full piece layout."""

    def __init__(self) -> None:
        """Initialize piece layout call tracking."""
        self.update_calls = 0

    def update(self) -> None:
        """Record that the layer refreshed layout data."""
        self.update_calls += 1

    def piece_item(self, piece: Piece, square: Square) -> ImageSquareItem:
        """Return a normal piece image item for ``piece`` and ``square``."""
        return layer_image_item(f"piece:{piece.kind.text}:{square.file.text}{square.rank.text}")

    def drag_item(self, piece: Piece, square: Square, coord: Coord) -> ImageSquareItem:
        """Return a dragged piece image item centered at ``coord``."""
        _ = square
        return ImageSquareItem(
            ImageAsset(f"drag:{piece.kind.text}", 1, 1),
            Rect(coord.x - 5, coord.y - 5, 10, 10),
        )


class PromotionLayoutSpy:
    """Provide promotion render items without constructing full promotion layout."""

    def __init__(self) -> None:
        """Initialize promotion layout call tracking."""
        self.update_calls = 0

    def update(self) -> None:
        """Record that the layer refreshed layout data."""
        self.update_calls += 1

    def fill_item(self, square: Square, index: int) -> ColorSquareItem:
        """Return a normal promotion fill item."""
        _ = square
        return ColorSquareItem(Color(index, 0, 0), LAYER_RECT)

    def highlight_fill_item(self, square: Square, index: int) -> ColorSquareItem:
        """Return a highlighted promotion fill item."""
        _ = square
        return ColorSquareItem(Color(99, index, 0), LAYER_RECT)

    def piece_item(self, square: Square, index: int, piece: Piece) -> ImageSquareItem:
        """Return a promotion piece image item."""
        _ = square
        return layer_image_item(f"promotion:{index}:{piece.kind.text}")


def image_paths(renderer: NullRenderer) -> list[str]:
    """Return image asset paths emitted by a null renderer."""
    return [
        str(command.item.image_asset) for command in renderer.commands if isinstance(command, DrawSquareImageCommand)
    ]


class GameAdapterProxyAdapterSpy:
    """Adapter fake that records game-state calls and returns configured values."""

    def __init__(self, label: str) -> None:
        """Initialize the fake with distinct return values for delegation assertions."""
        self.label = label
        self.default_fen = f"{label} default"
        self.fen = f"{label} fen"
        self.turn = PlayerColor.WHITE
        self.move_history = (Move(Square(0, 1), Square(0, 2)),)
        self.placement = {Square(0, 0): Piece(PlayerColor.WHITE, PieceKind.KING)}
        self.king_square = Square(4, 0)
        self.legal_hints = {Square(1, 0)}
        self.pseudo_hints = {Square(2, 0)}
        self.is_legal = True
        self.is_promotion = False
        self.has_history = True
        self.in_check = False
        self.in_checkmate = False
        self.calls: list[tuple[str, object]] = []

    def pieces(self) -> dict[Square, Piece]:
        """Return the configured piece mapping."""
        self.calls.append(("pieces", ()))
        return dict(self.placement)

    def piece_at(self, square: Square) -> Piece | None:
        """Return the piece configured on ``square``."""
        self.calls.append(("piece_at", square))
        return self.placement.get(square)

    def set_piece(self, square: Square, piece: Piece | None) -> None:
        """Record piece placement updates."""
        self.calls.append(("set_piece", (square, piece)))
        if piece is None:
            self.placement.pop(square, None)
            return
        self.placement[square] = piece

    def king(self, color: PlayerColor) -> Square | None:
        """Return the configured king square."""
        self.calls.append(("king", color))
        return self.king_square

    def is_legal_move(self, move: Move) -> bool:
        """Return the configured legality flag."""
        self.calls.append(("is_legal_move", move))
        return self.is_legal

    def is_promotion_move(self, move: Move) -> bool:
        """Return the configured promotion flag."""
        self.calls.append(("is_promotion_move", move))
        return self.is_promotion

    def has_move_history(self) -> bool:
        """Return the configured move-history flag."""
        self.calls.append(("has_move_history", ()))
        return self.has_history

    def move(self, move: Move) -> None:
        """Record applied non-promotion moves."""
        self.calls.append(("move", move))

    def is_check(self) -> bool:
        """Return the configured check flag."""
        self.calls.append(("is_check", ()))
        return self.in_check

    def is_checkmate(self) -> bool:
        """Return the configured checkmate flag."""
        self.calls.append(("is_checkmate", ()))
        return self.in_checkmate

    def get_legal_hints(self, square: Square) -> set[Square]:
        """Return configured legal hint squares."""
        self.calls.append(("get_legal_hints", square))
        return set(self.legal_hints)

    def get_pseudo_legal_hints(self, square: Square, color: PlayerColor) -> set[Square]:
        """Return configured pseudo-legal hint squares."""
        self.calls.append(("get_pseudo_legal_hints", (square, color)))
        return set(self.pseudo_hints)


class ControllerProxySpy:
    """Controller fake that records calls and returns configurable results."""

    def __init__(self, label: str) -> None:
        """Initialize the spy with a label used in recorded calls."""
        self.label = label
        self.calls: list[tuple[str, tuple[Any, ...]]] = []
        self.press_result = ControllerEventResult(handled=True)
        self.outside_press_result = ControllerEventResult(requires_render=True)
        self.move_result = ControllerEventResult(handled=True, requires_render=True)
        self.outside_move_result = ControllerEventResult()
        self.release_result = ControllerEventResult(handled=True)
        self.outside_release_result = ControllerEventResult(requires_render=True)

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
    ) -> ControllerProxySpy:
        """Create a spy while ignoring collaborators that are irrelevant to proxy delegation."""
        return cls("created")

    def on_press(self, coord: Coord, button: MouseButton, modifier: Modifier | None = None) -> ControllerEventResult:
        """Record press calls exactly as the proxy forwards them."""
        self.calls.append(("press", (coord, button, modifier)))
        return self.press_result

    def on_press_outside_view(self) -> ControllerEventResult:
        """Record outside press cleanup calls."""
        self.calls.append(("press_outside", ()))
        return self.outside_press_result

    def on_pointer_move(self, coord: Coord, modifier: Modifier | None = None) -> ControllerEventResult:
        """Record pointer move calls exactly as the proxy forwards them."""
        self.calls.append(("move", (coord, modifier)))
        return self.move_result

    def on_pointer_move_outside_view(self) -> ControllerEventResult:
        """Record outside pointer move cleanup calls."""
        self.calls.append(("move_outside", ()))
        return self.outside_move_result

    def on_release(self, coord: Coord, button: MouseButton, modifier: Modifier | None = None) -> ControllerEventResult:
        """Record release calls exactly as the proxy forwards them."""
        self.calls.append(("release", (coord, button, modifier)))
        return self.release_result

    def on_release_outside_view(self) -> ControllerEventResult:
        """Record outside release cleanup calls."""
        self.calls.append(("release_outside", ()))
        return self.outside_release_result


STANDARD_CONTROLLER_ORIGIN = Square(File.B, Rank.TWO)
"""Origin square used by controller annotation tests."""
STANDARD_CONTROLLER_TARGET = Square(File.F, Rank.SIX)
"""Target square used by controller annotation tests."""
STANDARD_CONTROLLER_ORIGIN_COORD = Coord(10, 20)
"""Viewport coordinate mapped to ``STANDARD_CONTROLLER_ORIGIN``."""
STANDARD_CONTROLLER_TARGET_COORD = Coord(30, 40)
"""Viewport coordinate mapped to ``STANDARD_CONTROLLER_TARGET``."""


class StandardControllerQuerySpy:
    """Map fixed coordinates to squares and record query calls."""

    def __init__(self, squares: dict[tuple[int, int], Square | None]) -> None:
        """Store the coordinate-to-square mapping used by the fake query."""
        self.squares = squares
        self.calls: list[tuple[str, int, int]] = []

    def square_at(self, x: int, y: int) -> Square | None:
        """Return the configured square for ``x`` and ``y``."""
        self.calls.append(("square_at", x, y))
        return self.squares.get((x, y))


class StandardControllerAnnotationSpy:
    """Record annotation session calls made by the controller."""

    def __init__(self) -> None:
        """Initialize empty annotation call history."""
        self.calls: list[tuple[object, ...]] = []

    def set_circle_preview(self, circle_type: object, square: Square) -> None:
        """Record a circle preview request."""
        self.calls.append(("set_circle_preview", circle_type, square))

    def set_arrow_preview(
        self, arrow_type: object, from_square: Square, to_square: Square, has_corner: bool = False
    ) -> None:
        """Record an arrow preview request."""
        self.calls.append(("set_arrow_preview", arrow_type, from_square, to_square, has_corner))

    def clear_preview(self) -> None:
        """Record preview cleanup."""
        self.calls.append(("clear_preview",))

    def add_circle(self, circle_type: object, square: Square) -> None:
        """Record a circle commit request."""
        self.calls.append(("add_circle", circle_type, square))

    def remove_circle(self, square: Square) -> None:
        """Record a circle removal request."""
        self.calls.append(("remove_circle", square))

    def add_arrow(self, arrow_type: object, from_square: Square, to_square: Square, has_corner: bool = False) -> None:
        """Record an arrow commit request."""
        self.calls.append(("add_arrow", arrow_type, from_square, to_square, has_corner))

    def remove_arrow(self, from_square: Square, to_square: Square) -> None:
        """Record an arrow removal request."""
        self.calls.append(("remove_arrow", from_square, to_square))

    def remove_hint_arrow(self, from_square: Square, to_square: Square) -> None:
        """Record an unexpected hint-arrow removal request."""
        self.calls.append(("remove_hint_arrow", from_square, to_square))


class StandardControllerGameStub:
    """Provide the game methods the controller may call in these tests."""

    def __init__(self) -> None:
        """Initialize a game stub with an empty board."""
        self.turn = PlayerColor.WHITE
        self.pieces: dict[Square, Piece] = {}
        self.legal_moves: set[Move] = set()
        self.moves: list[Move] = []
        self.checkmate = False

    def piece_at(self, square: Square) -> Piece | None:
        """Return the configured piece at ``square``."""
        return self.pieces.get(square)

    def is_legal_move(self, move: Move) -> bool:
        """Return whether ``move`` was configured as legal."""
        return move in self.legal_moves

    def move(self, move: Move) -> None:
        """Record an applied move."""
        self.moves.append(move)

    def is_checkmate(self) -> bool:
        """Return the configured checkmate status."""
        return self.checkmate


class StandardControllerInteractionSpy:
    """Record selection and drag calls made by the controller."""

    def __init__(self) -> None:
        """Initialize empty interaction state."""
        self.calls: list[tuple[object, ...]] = []
        self.selected: SquareData | None = None
        self.active_drag = False

    def clear_selection(self) -> None:
        """Record selection cleanup."""
        self.calls.append(("clear_selection",))
        self.selected = None

    def has_active_drag(self) -> bool:
        """Return whether a drag is configured as active."""
        return self.active_drag

    def update_drag(self, coord: Coord) -> None:
        """Record a drag update."""
        self.calls.append(("update_drag", coord))

    def clear_drag(self) -> None:
        """Record drag cleanup."""
        self.calls.append(("clear_drag",))
        self.active_drag = False

    def get_selected(self) -> SquareData | None:
        """Return the configured selected square data."""
        return self.selected

    def select_piece(self, square: Square) -> None:
        """Record a selection request."""
        self.calls.append(("select_piece", square))
        self.selected = SquareData(square, Piece(PlayerColor.WHITE, PieceKind.PAWN))

    def begin_drag(self, square: Square, coord: Coord) -> None:
        """Record a drag start."""
        self.calls.append(("begin_drag", square, coord))
        self.active_drag = True


class StandardControllerPromotionSpy:
    """Record promotion calls and expose configurable active state."""

    def __init__(self, *, active: bool = False) -> None:
        """Store whether the promotion flow should start as active."""
        self.active = active
        self.calls: list[tuple[object, ...]] = []

    def has_active_promotion(self) -> bool:
        """Return whether promotion should take input priority."""
        return self.active

    def is_promotion_move(self, move: Move) -> bool:
        """Return ``False`` because annotation tests do not exercise promotion moves."""
        _ = move
        return False

    def show_promotion(self, move: Move, color: PlayerColor, coord: Coord) -> None:
        """Record a promotion display request."""
        self.calls.append(("show_promotion", move, color, coord))
        self.active = True

    def update_promotion_highlight(self, coord: Coord) -> None:
        """Record a promotion highlight update."""
        self.calls.append(("update_promotion_highlight", coord))

    def commit_promotion(self, coord: Coord) -> None:
        """Record a promotion commit request."""
        self.calls.append(("commit_promotion", coord))

    def clear_promotion_highlight(self) -> None:
        """Record promotion highlight cleanup."""
        self.calls.append(("clear_promotion_highlight",))


class StandardControllerHarness:
    """Bundle the controller with its faked collaborators."""

    def __init__(self, *, annotations_enabled: bool = True, promotion_active: bool = False) -> None:
        """Create a controller with local spies and deterministic square lookup."""
        self.view_state = ViewState(PlayerColor.WHITE)
        self.view_state.annotations_enabled = annotations_enabled
        self.query = StandardControllerQuerySpy(
            {
                (STANDARD_CONTROLLER_ORIGIN_COORD.x, STANDARD_CONTROLLER_ORIGIN_COORD.y): STANDARD_CONTROLLER_ORIGIN,
                (STANDARD_CONTROLLER_TARGET_COORD.x, STANDARD_CONTROLLER_TARGET_COORD.y): STANDARD_CONTROLLER_TARGET,
            }
        )
        self.annotation = StandardControllerAnnotationSpy()
        self.game = StandardControllerGameStub()
        self.interaction = StandardControllerInteractionSpy()
        self.promotion = StandardControllerPromotionSpy(active=promotion_active)
        self.controller = StandardChessController.create(
            view_state=self.view_state,
            game=cast("GameSessionProtocol", self.game),
            interaction=cast("InteractionSessionProtocol", self.interaction),
            annotation=cast("AnnotationSessionProtocol", self.annotation),
            promotion=cast("PromotionSessionProtocol", self.promotion),
            query=cast("BoardQuery", self.query),
        )
