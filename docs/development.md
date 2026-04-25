# Development Guide

This document describes the workspace layout, development workflow, and runtime architecture.

## Table of Contents

1. [Workspace Layout](#workspace-layout)
1. [Core Package Structure](#core-package-structure)
1. [Qt Module Structure](#qt-module-structure)
1. [Runtime Assembly](#runtime-assembly)
1. [Game Configuration](#game-configuration)
1. [Development Environment](#development-environment)
1. [Assets](#assets)
1. [Tests](#tests)
1. [Documentation Scope](#documentation-scope)

## Workspace Layout

The project is published as a single distribution named `pychessview`.

Source packages:

- `src/pychessview`: public package facade and import root
- `src/pychessview/engine`: backend-agnostic engine package
- `src/pychessview/qt`: optional Qt module exposed as `pychessview.qt`

Other top-level directories:

- `docs/`: project documentation
- `examples/`: runnable examples
- `tests/`: unit, integration, support, and shared test data
- `tools/`: development tooling and bootstrap scripts

## Core Package Structure

### Public API

- `src/pychessview/__init__.py` (`src/pychessview/engine/view.py`): public `View` API used to create and render a board
- `src/pychessview/__init__.py`: public exports for the engine facade

### Domain and Configuration

- `src/pychessview/engine/core/domain/`:
  - `GameSpec`: high-level configuration describing a game setup
  - `GameDefinition`: default position and promotion configuration
  - `GameAdapterProtocol`: contract for game backends
  - `ControllerProtocol`: contract for controller event routing

### Factories

- `src/pychessview/engine/factory/`:
  - constructs adapters and controllers from `GameSpec`
  - acts as the composition layer between configuration and runtime

### Runtime Components

- `src/pychessview/engine/core/session/`:
  - builds and owns the runtime (game session, interaction session, etc.)
  - wires together adapters, controllers, and state
  - coordinates runtime components during rendering and interaction

- `src/pychessview/engine/core/state/`:
  - mutable runtime state containers

- `src/pychessview/engine/core/query/`:
  - derived board data based on current state and layout
  - used by rendering and interaction layers

### Interaction

- `src/pychessview/engine/interaction/`:
  - controller implementations and controller protocols
  - input policy and event routing
  - translates input into session operations

### Layout and Geometry

- `src/pychessview/engine/layout/`:
  - geometry primitives
  - layout engine
  - board layout models

### Rendering

- `src/pychessview/engine/render/items/`:
  - value objects representing renderable elements

- `src/pychessview/engine/render/layers/`:
  - transforms state and layout into renderer calls

- `src/pychessview/engine/render/renderer/`:
  - `RendererProtocol`
  - null renderer implementation

### Themes and Assets

- `src/pychessview/engine/theme/`:
  - theme value objects
  - YAML-based theme loading

- `src/pychessview/assets/`:
  - static runtime assets, including SVGs, fonts, and default theme data

## Qt Module Structure

`src/pychessview/qt/` provides Qt integration:

- `widget/chessboard_widget.py`: public `ChessboardWidget`
- `widget/events.py`: Qt event helpers
- `renderer/qt_renderer.py`: Qt implementation of `RendererProtocol`
- `renderer/painter_adapter.py`: drawing adapter around `QPainter`
- `integration/qt_controller_adapter.py`: adapts Qt events to core controllers

## Runtime Assembly

The core runtime is assembled as follows:

1. `View(...)` calls `BoardSessionBuilder.build(...)`
1. The builder creates state objects, sessions, query helpers, render layers, controllers, and adapter proxies
1. `BoardSession` owns the assembled runtime
1. `render_frame(...)` computes layout and renders layers through the active renderer

Qt integration adds a wrapper:

1. `ChessboardWidget(...)` creates a `QtRenderer`
1. `ChessboardWidget(...)` creates a core `View`
1. `ChessboardWidget(...)` creates a `QtControllerAdapter`
1. `paintEvent(...)` forwards widget size to `View.render_frame(...)`
1. `QtControllerAdapter` normalizes mouse events and forwarded to the core controller

## Game Configuration

Game-specific behavior is defined through `GameSpec`.

`GameSpec` bundles:

- `definition`: default FEN and promotion configuration
- `theme_provider`: produces the active theme
- `adapter_factory`: creates the game adapter
- `controller_factory`: creates the controller

A `GameSpec` is typically constructed by a factory, such as
`StandardChessFactory`, which provides a complete and consistent configuration.

The `GameSpec` instance is passed to `View`, where it is used to construct the
runtime through session builders and factories.

`GameSpec` acts as the boundary between configuration and runtime assembly.

## Development Environment

### Bootstrap

Before running bootstrap:

- Ensure Python is installed and available in `PATH` (Python 3.11+).
- Ensure the `venv` module is available.
- If working in a Git repository:
  - `git`
  - `git-lfs`
  - `shellcheck`
  - PowerShell 7+ (`pwsh`) on Windows

Bootstrap scripts are located in `tools/`:

- `tools\bootstrap_dev.ps1`
- `tools\bootstrap_dev.bat`
- `tools/bootstrap_dev.sh`

The bootstrap process:

- creates or recreates `.venv`
- installs dependencies
- installs pre-commit hooks when `.git` is present
- prepares Git LFS assets when `.git` is present
- cleans Python cache directories

Run the appropriate script:

```powershell
powershell -ExecutionPolicy Bypass -File tools\bootstrap_dev.ps1
```

```cmd
tools\bootstrap_dev.bat
```

```bash
sh tools/bootstrap_dev.sh
```

### Activate the Virtual Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

```cmd
.venv\Scripts\activate.bat
```

```bash
source .venv/bin/activate
```

### Development Commands

The development command entry point can be run as a module:

```shell
python -m tools.devtools --help
```

## Assets

Theme assets are located in:

`src/pychessview/assets/`

They include:

- piece SVGs
- board assets
- highlight assets
- fonts
- default theme configuration

Assets may be stored using Git LFS. Ensure LFS files are checked out correctly:

```shell
git lfs install
git lfs pull
git lfs checkout
```

## Tests

Tests are located in:

- `tests/unit/`
- `tests/integration/`

### Unit Test Requirements

- Isolate a single function, class, or method
- Must not depend on real subsystems unless required
- Replace dependencies with fakes, stubs, or simple spies where useful
- Cover the behavior, and contract
- Mark with `pytestmark = pytest.mark.unit`

### Integration Test Requirements

- Test collaboration between real components
- Interact with the system under test through `tests/support/`
- Mark with `pytestmark = pytest.mark.integration`

### Test Organization

- Mirror the structure of `src/`
- Use one test file per module when possible
- Use shared helpers
- Store shared test data under `tests/data/`

## Documentation Scope

Documentation is split by audience:

- [README.md](../README.md): high-level overview
- [docs/engine.md](engine.md): engine usage
- [docs/qt_widget.md](qt_widget.md): Qt integration
- [docs/development.md](development.md): architecture and workflow
