# Engine Guide

This document describes how to integrate the backend-agnostic engine from the
`pychessview` package into an application.

## Table of Contents

1. [Overview](#overview)
1. [Conceptual Model](#conceptual-model)
1. [Getting Started](#getting-started)
   1. [Install](#install)
   1. [Import](#import)
   1. [Renderer](#renderer)
   1. [Typical Integration Flow](#typical-integration-flow)
   1. [Integration Reference](#integration-reference)
1. [Engine View API](#engine-view-api)
   1. [Constructor](#constructor)
   1. [Public Properties](#public-properties)
   1. [Public Methods](#public-methods)
1. [Settings](#settings)
1. [Themes](#themes)
1. [Game Specifications](#game-specifications)
1. [Customization](#customization)
   1. [Custom Game Specification](#custom-game-specification)
   1. [Custom Controller](#custom-controller)
   1. [Custom Game Adapter](#custom-game-adapter)
   1. [Custom Theme](#custom-theme)
1. [Usage Notes](#usage-notes)

## Overview

The primary public entry point for the engine is `View`.

`View` is responsible for:

- connecting the pychessview runtime to a renderer
- loading game-specific configuration through `GameSpec`
- exposing mutable board and interaction settings through `ViewState`
- coordinating game, interaction, annotation, and promotion sessions
- rendering the current frame

The engine is backend-agnostic. It does not depend on a specific GUI
framework. A concrete integration must:

- provide a renderer implementing `RendererProtocol`
- forward pointer input to `view.controller`

## Conceptual Model

At runtime, the system is structured in layers:

- `View` orchestrates the entire runtime
- Sessions manage state and behavior:
  - `game`: move execution and position state
  - `interaction`: highlights and drag state
  - `annotation`: arrows and circles
  - `promotion`: promotion flow
- The controller translates input into changes
- The game adapter provides board state and chess rules
- The renderer produces the final visual output

Data flows downward:

```text
GameSpec -> View -> Session(s) -> Renderer
```

Input flows upward:

```text
UI -> Controller -> Session(s) -> Layout -> Renderer
```

## Getting Started

### Install

Install the published package from PyPI:

```shell
python -m pip install pychessview
```

Install the package from the workspace:

```shell
python -m pip install .
```

Install the package directly from a Git repository:

```shell
python -m pip install "pychessview @ git+https://github.com/Diblo/pychessview.git"
```

### Import

`View` and game specification factories are exported from `pychessview`.

```python
from pychessview import StandardChessFactory, View
```

### Renderer

A renderer must implement `RendererProtocol`.

The renderer is a passive output layer:

- it does not maintain state
- it does not calculate layout or rules
- it only draws what it is given

Minimal skeleton:

```python
from pychessview import RendererProtocol


class ExampleRenderer(RendererProtocol):
    def begin_frame(self, viewport) -> None:
        ...

    def draw_square_color(self, item) -> None:
        ...

    def draw_square_image(self, item) -> None:
        ...

    def draw_text_ink(self, item) -> None:
        ...

    def draw_circle(self, item, color) -> None:
        ...

    def draw_arrow(self, item, color, points) -> None:
        ...

    def end_frame(self) -> None:
        ...
```

A renderer implementation is expected to translate given data into calls for the target backend.

For testing or inspection, `NullRenderer` can be used.

### Typical Integration Flow

Typical integration follows this pattern:

1. Create a renderer bound to the UI framework.
1. Create a `GameSpec` or use a predefined game factory.
1. Construct `View`.
1. Forward pointer events to `view.controller`.
1. Call `render_frame(...)` when:
   - the viewport changes
   - the game state changes
   - interaction or presentation settings change

Example:

```python
from pychessview import StandardChessFactory, View
from pychessview.engine.core.primitives import PlayerColor
from pychessview.engine.render.renderer.null_renderer import NullRenderer

renderer = NullRenderer()
game_spec = StandardChessFactory.create_game_spec()

view = View(
    renderer=renderer,
    game_spec=game_spec,
    width=640,
    height=640,
    player=PlayerColor.WHITE,
)

view.render_frame()
```

A real integration should provide a renderer that draws to the target backend
and should forward pointer events to `view.controller`.

### Integration Reference

| Goal                    | API                                                                  |
| ----------------------- | -------------------------------------------------------------------- |
| Create and render board | `View(...)`, `render_frame(...)`                                     |
| Change settings         | `view.settings`                                                      |
| Load position           | `load_position_from_fen(...)`, `reset_board(...)`                    |
| Switch game variation   | `load_game(...)`                                                     |
| Access runtime behavior | `view.game`, `view.interaction`, `view.annotation`                   |
| Query board space       | `view.query`                                                         |
| Change theme            | `view.theme` or `load_theme(...)`                                    |
| Enable/disable input    | `view.controller_enabled`                                            |

## Engine View API

### Constructor

```python
class View:
    def __init__(
        self,
        renderer: RendererProtocol,
        game_spec: GameSpec,
        width: int = 1,
        height: int = 1,
        x: int = 0,
        y: int = 0,
        *,
        player: PlayerColor = PlayerColor.WHITE,
        default_fen: str | None = None,
        white_promotion_pieces: tuple[Piece, ...] | None = None,
        black_promotion_pieces: tuple[Piece, ...] | None = None,
        game_session_class: type[GameSessionProtocol] | None = None,
        interaction_session_class: type[InteractionSessionProtocol] | None = None,
        annotation_session_class: type[AnnotationSessionProtocol] | None = None,
        promotion_session_class: type[PromotionSessionProtocol] | None = None,
    ) -> None: ...
```

| Argument                                           | Description                                                                   |
| -------------------------------------------------- | ----------------------------------------------------------------------------- |
| `renderer`                                         | Renderer implementation used to draw each frame.                              |
| `game_spec`                                        | Active game configuration used to construct adapters, controllers, and theme. |
| `width`, `height`, `x`, `y`                        | Initial viewport size and position.                                           |
| `player`                                           | Initial orientation and default interaction player.                           |
| `default_fen`                                      | Optional starting position override.                                          |
| `white_promotion_pieces`, `black_promotion_pieces` | Optional promotion option overrides.                                          |
| session class overrides                            | Advanced customization hooks for replacing default runtime behavior.          |

### Public Properties

| Property             | Description                                          |
| -------------------- | ---------------------------------------------------- |
| `theme`              | Active rendering theme                               |
| `settings`           | `ViewState` controlling presentation and interaction |
| `fen`                | Current position                                     |
| `game`               | Game session (moves, position state)                 |
| `interaction`        | Interaction session (highlight, drag)                |
| `annotation`         | Annotation session (arrows and circles)              |
| `query`              | Board query helper                                   |
| `controller_enabled` | Enable/disable controller                            |
| `controller`         | Input controller                                     |

### Public Methods

| Method                        | Description                                                          |
| ----------------------------- | -------------------------------------------------------------------- |
| `load_game(...)`              | Rebuild runtime with a new `GameSpec`                                |
| `load_position_from_fen(fen)` | Replace the current position without resetting the active game state |
| `reset_board(fen=None)`       | Reset to default or given FEN                                        |
| `render_frame(...)`           | Update viewport and render                                           |

## Settings

`view.settings` exposes `ViewState`.

| Property                             | Description                                                                         |
| ------------------------------------ | ----------------------------------------------------------------------------------- |
| `player`                             | Player color used for orientation and interaction defaults                          |
| `restrict_to_player_pieces`          | Restrict both selection and move execution to pieces owned by the configured player |
| `restrict_to_select_opponent_pieces` | Allow selecting opponent pieces for inspection; move execution remains disallowed   |
| `show_player_hints`                  | Show legal and pseudo-legal hints for the configured player                         |
| `show_opponent_hints`                | Show legal and pseudo-legal hints for the opponent                                  |
| `annotations_enabled`                | Enable or disable annotation interactions                                           |
| `show_border`                        | Show or hide the board border                                                       |
| `stretch_to_fit`                     | Stretch the board to fill the viewport instead of keeping it square                 |
| `white_at_bottom`                    | Control whether White is shown at the bottom of the board                           |
| `show_labels`                        | Show or hide rank and file labels                                                   |
| `rotate_labels`                      | Rotate labels with board orientation                                                |
| `label_side_visibility`              | Visibility flags for top, right, bottom, and left labels                            |

| Method                                                           | Description                                            |
| ---------------------------------------------------------------- | ------------------------------------------------------ |
| `set_sides_visibility(top=..., right=..., bottom=..., left=...)` | Update one or more label-edge visibility flags         |
| `set_side_visibility(side, enabled)`                             | Update label visibility for a single board edge        |
| `is_label_side_visible(side)`                                    | Query whether labels are visible on a given board edge |

Example:

```python
view.settings.show_border = False
view.settings.white_at_bottom = False
```

## Themes

Themes define visual assets.

Built-in theme:

```python
from pychessview import load_theme, ThemeName

view.theme = load_theme(ThemeName.STANDARD_CHESS)
```

Or from file:

```python
view.theme = load_theme("path/to/theme/settings.yaml")
```

## Game Specifications

`GameSpec` defines how the runtime is constructed.

It bundles:

- `definition`: default FEN and promotion options
- `theme_provider`
- `adapter_factory`
- `controller_factory`

Built-in `GameSpec` is created by a factory.

Example:

```python
from pychessview import StandardChessFactory

game_spec = StandardChessFactory.create_game_spec()
```

A different starting position can be supplied when the game specification is
created:

```python
from pychessview import StandardChessFactory

game_spec = StandardChessFactory.create_game_spec(
    default_fen="8/8/8/8/8/8/8/K6k w - - 0 1"
)
```

## Customization

### Custom Game Specification

Custom variants are created by implementing:

- `ThemeProviderProtocol`: produces the theme
- `GameAdapterFactoryProtocol`: creates the game adapter
- `ControllerFactoryProtocol`: creates the controller

and combining them into a `GameSpec`.

This example builds a minimal `GameSpec` by combining a game definition with
explicit theme, adapter, and controller factories.

```python
from pychessview import GameDefinition, GameSpec
from pychessview.engine.core.primitives import Piece, PieceKind, PlayerColor
from pychessview.engine.factory.null_game import NullControllerFactory, NullGameAdapterFactory, NullThemeProvider

default_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
game_spec = GameSpec(
    definition=GameDefinition(
        default_fen,
        (
            Piece(PlayerColor.WHITE, PieceKind.QUEEN),
            Piece(PlayerColor.WHITE, PieceKind.ROOK),
            Piece(PlayerColor.WHITE, PieceKind.BISHOP),
            Piece(PlayerColor.WHITE, PieceKind.KNIGHT),
        ),
        (
            Piece(PlayerColor.BLACK, PieceKind.QUEEN),
            Piece(PlayerColor.BLACK, PieceKind.ROOK),
            Piece(PlayerColor.BLACK, PieceKind.BISHOP),
            Piece(PlayerColor.BLACK, PieceKind.KNIGHT),
        ),
    ),
    theme_provider=NullThemeProvider(),
    adapter_factory=NullGameAdapterFactory.create(default_fen),
    controller_factory=NullControllerFactory(),
)
```

### Custom Controller

A custom controller is defined by implementing `ControllerProtocol`.

The controller translates pointer input into runtime state updates and game actions.

#### Construction

Controllers are not instantiated directly by the integration layer. Instead,
they are created through the `create(...)` classmethod.

The runtime provides all required collaborators:

- `view_state`: mutable presentation and interaction settings
- `game`: game session for move execution and position state
- `interaction`: manages selection and drag state
- `annotation`: manages arrows and circles
- `promotion`: manages active promotion choices
- `query`: helper for mapping coordinates to board-space

A controller implementation typically stores these dependencies and uses them
during event handling.

#### Event Contract

Each event method returns a `ControllerEventResult`:

- `handled=True`: the controller consumed the event
- `handled=False`: the event produced no controller action
- `requires_render=True`: the caller should trigger a render pass
- `requires_render=False`: no render pass is required

Event methods are called as follows:

- `on_press(...)`: pointer pressed inside the board
- `on_pointer_move(...)`: pointer moved
- `on_release(...)`: pointer released
- `*_outside_view`: same events occurring outside the board area

#### Example

```python
from pychessview import ControllerProtocol
from pychessview.engine.interaction.controller_event_result import ControllerEventResult
from pychessview.engine.interaction.input.mouse_buttons import MouseButton
from pychessview.engine.layout.primitives import Coord
from pychessview.engine.interaction.input.modifiers import Modifier
from pychessview.engine.core.session.protocols import (
    AnnotationSessionProtocol,
    GameSessionProtocol,
    InteractionSessionProtocol,
    PromotionSessionProtocol,
)
from pychessview.engine.core.state.view_state import ViewState
from pychessview.engine.core.query.board_query import BoardQuery

class PassiveController(ControllerProtocol):
    """Controller that ignores all pointer input."""

    def __init__(self) -> None:
        """Initialize the controller.

        This implementation does not use any collaborators.
        """

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
    ) -> "PassiveController":
        """Create a controller instance.

        This implementation ignores all provided collaborators.
        """
        return cls()

    def on_press(
        self,
        coord: Coord,
        button: MouseButton,
        modifier: Modifier | None = None,
    ) -> ControllerEventResult:
        _ = coord, modifier, button
        return ControllerEventResult(handled=True)

    def on_press_outside_view(self) -> ControllerEventResult:
        return ControllerEventResult()

    def on_pointer_move(self, coord: Coord, modifier: Modifier | None = None) -> ControllerEventResult:
        return ControllerEventResult(handled=True)

    def on_pointer_move_outside_view(self) -> ControllerEventResult:
        return ControllerEventResult()

    def on_release(
        self,
        coord: Coord,
        button: MouseButton,
        modifier: Modifier | None = None,
    ) -> ControllerEventResult:
        _ = coord, modifier, button
        return ControllerEventResult(handled=True)

    def on_release_outside_view(self) -> ControllerEventResult:
        return ControllerEventResult()
```

### Custom Game Adapter

A custom game adapter is defined by implementing `GameAdapterProtocol`.

The adapter is responsible for exposing board state, move validation, move
execution, king lookup, and move hints in the shape expected by the runtime.

#### Adapter Example

```python
from pychessview import GameAdapterProtocol
from pychessview.engine.core.primitives import Move, Piece, PieceKind, PlayerColor, Square


class SimpleGameAdapter(GameAdapterProtocol):
    """Minimal adapter backed by an internal piece mapping.

    This example is intentionally incomplete as chess logic. It demonstrates the
    adapter contract, not a full chess implementation.
    """

    def __init__(self, default_fen: str) -> None:
        """Initialize the adapter with a default FEN.

        This constructor is specific to this implementation. Construction is not
        defined by ``GameAdapterProtocol``. A ``default_fen`` argument is a
        common choice because ``GameAdapterFactoryProtocol`` provides the default
        FEN when creating an adapter.
        """
        self._default_fen = default_fen
        self._fen = default_fen
        self._pieces: dict[Square, Piece] = {}

    @property
    def default_fen(self) -> str:
        return self._default_fen

    @default_fen.setter
    def default_fen(self, fen: str) -> None:
        self._default_fen = fen

    @property
    def fen(self) -> str:
        return self._fen

    @fen.setter
    def fen(self, fen: str) -> None:
        self._fen = fen
        self._pieces.clear()

    @property
    def turn(self) -> PlayerColor:
        return PlayerColor.WHITE

    def pieces(self) -> dict[Square, Piece]:
        return dict(self._pieces)

    def piece_at(self, square: Square) -> Piece | None:
        return self._pieces.get(square)

    def set_piece(self, square: Square, piece: Piece | None) -> None:
        if piece is None:
            self._pieces.pop(square, None)
            return
        self._pieces[square] = piece

    def king(self, color: PlayerColor) -> Square | None:
        for square, piece in self._pieces.items():
            if piece.color == color and piece.kind is PieceKind.KING:
                return square
        return None

    def is_legal_move(self, move: Move, promote: Piece | None = None) -> bool:
        return move.from_square in self._pieces

    def is_promotion_move(self, move: Move) -> bool:
        return False

    def has_move_history(self) -> bool:
        return False

    @property
    def move_history(self) -> tuple[Move, ...]:
        return ()

    def move(self, move: Move) -> None:
        piece = self._pieces.pop(move.from_square, None)
        if piece is not None:
            self._pieces[move.to_square] = piece

    def promote(self, move: Move, piece: Piece) -> None:
        self._pieces.pop(move.from_square, None)
        self._pieces[move.to_square] = piece

    def is_check(self) -> bool:
        return False

    def is_checkmate(self) -> bool:
        return False

    def get_legal_hints(self, square: Square) -> set[Square]:
        return set()

    def get_pseudo_legal_hints(self, square: Square, color: PlayerColor) -> set[Square]:
        return set()
```

This example stores board state in a simple mapping and does not enforce chess
rules beyond the minimal method contract. It is useful as a structural example
of the adapter API, but not as a production-ready chess backend.

### Custom Theme

Themes are defined via a `settings.yaml` and assets.

Typical workflow:

1. Copy the default theme assets into a new theme folder.
1. Edit `settings.yaml` and the referenced assets.
1. Keep asset paths relative to the `settings.yaml` location.
1. Load the new theme with `load_theme(...)` and assign it to `view.theme`.

Example:

```python
from pychessview import StandardChessFactory, View, load_theme
from pychessview.engine.render.renderer.null_renderer import NullRenderer

view = View(
    renderer=NullRenderer(),
    game_spec=StandardChessFactory.create_game_spec(),
    width=512,
    height=512,
)

view.theme = load_theme("path/to/custom/theme/settings.yaml")
view.render_frame()
```

## Usage Notes

| Topic                  | Note                                                                                                                                     |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Rendering              | Nothing is drawn until `render_frame(...)` is called                                                                                     |
| Resizing               | Update the viewport via `render_frame(...)`                                                                                              |
| Theme                  | Mutate the active theme for incremental changes, or assign a new theme through `view.theme = load_theme(...)` when replacing it entirely |
| Game variant switching | Use `load_game(...)` to rebuild the runtime with a new `GameSpec`                                                                        |
| Position loading       | Use `load_position_from_fen(...)` or `reset_board(...)` to move to a known position                                                      |
| Input handling         | Pointer events must be forwarded to `view.controller`                                                                                    |
