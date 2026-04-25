# Qt Widget

This document describes the optional Qt widget module built on top of `pychessview`.

## Table of Contents

1. [Overview](#overview)
1. [Requirements](#requirements)
1. [Install](#install)
1. [Quick Start](#quick-start)
1. [Widget Construction](#widget-construction)
1. [Public Widget API](#public-widget-api)
1. [Settings and Sessions](#settings-and-sessions)
1. [Input Handling](#input-handling)
1. [Painting](#painting)
1. [Themes and Assets](#themes-and-assets)
1. [Demo](#demo)

## Overview

`pychessview.qt` provides a Qt `QWidget` integration for the backend-agnostic
`pychessview` package.

The main public entry points are:

- `pychessview.qt.ChessboardWidget`
- `pychessview.StandardChessFactory`
- `pychessview.load_theme`
- `pychessview.ThemeName`

`ChessboardWidget` wraps the `View` core and connects it to Qt-specific rendering
and mouse-event handling.

## Requirements

- Python 3.11+
- `PySide6`

## Install

Install the published package with the Qt extra from PyPI:

```shell
python -m pip install "pychessview[qt]"
```

Install the package with the Qt extra from the workspace:

```shell
python -m pip install ".[qt]"
```

Install the package with the Qt extra directly from a Git repository:

```shell
python -m pip install "pychessview[qt] @ git+https://github.com/Diblo/pychessview.git"
```

## Quick Start

```python
from PySide6.QtWidgets import QApplication

from pychessview import StandardChessFactory
from pychessview.qt import ChessboardWidget


def main() -> int:
    app = QApplication.instance() or QApplication([])

    widget = ChessboardWidget(game_spec=StandardChessFactory.create_game_spec())
    widget.setWindowTitle("ChessboardWidget Qt Demo")
    widget.resize(640, 640)
    widget.show()

    return app.exec()
```

## Widget Construction

`ChessboardWidget` constructs and owns:

- a `QtRenderer`
- a core `View`
- a `QtControllerAdapter`

The widget delegates board state and runtime behavior to the underlying core
`View`, while Qt-specific painting and mouse handling stay in the widget layer.

Constructor arguments:

- `parent`: optional Qt parent object
- `game_spec`: required `GameSpec`
- `player`: initial player orientation
- `default_fen`: optional initial position override
- `white_promotion_pieces`, `black_promotion_pieces`: optional promotion
  overrides
- `game_session_class`, `interaction_session_class`,
  `annotation_session_class`, `promotion_session_class`: optional core session
  overrides

## Public Widget API

Properties:

- `theme`
- `settings`
- `fen`
- `game`
- `interaction`
- `annotation`
- `query`
- `controller_enabled`

Methods:

- `load_game(...)`
- `load_position_from_fen(fen)`
- `reset_board(fen=None)`
- `sizeHint()`
- `minimumSizeHint()`

The widget forwards these stateful operations to the underlying core `View`.

## Settings and Sessions

`widget.settings` exposes the same `ViewState` object as `View.settings`.

That means the same presentation and interaction flags are available from the
Qt widget, for example:

```python
widget.settings.show_border = True
widget.settings.show_labels = True
widget.settings.restrict_to_player_pieces = False
widget.settings.annotations_enabled = True
```

The session and helper properties expose the same runtime objects as the core
API:

- `widget.game`
- `widget.interaction`
- `widget.annotation`
- `widget.query`

## Input Handling

`ChessboardWidget` translates Qt mouse events into core controller calls through
`QtControllerAdapter`.

Handled events:

- `mousePressEvent(...)`
- `mouseMoveEvent(...)`
- `mouseReleaseEvent(...)`

Controller methods return `ControllerEventResult`. The widget uses
`requires_render=True` to schedule a repaint and `handled=True` to consume the
Qt event. The controller return value is not a plain boolean.

When `controller_enabled` is `False`, the underlying core controller is disabled
and the widget stops performing normal board interaction.

## Painting

Painting is handled in `paintEvent(...)`:

1. a `QPainter` is created for the widget
1. the painter is passed to `QtRenderer`
1. the underlying `View` renders a frame using the widget size

This means repaint and resize naturally drive board rendering.

## Themes and Assets

The widget uses the same theme system as the core package.

Built-in theme:

```python
from pychessview import ThemeName, load_theme

widget.theme = load_theme(ThemeName.STANDARD_CHESS)
```

Custom theme:

```python
widget.theme = load_theme("path/to/theme/settings.yaml")
```

Theme assets, including fonts and images under
`src/pychessview/assets/`, are runtime inputs. In a
normal clone they may be backed by Git LFS.

## Demo

The runnable example lives in `examples/qt_demo.py`.

Run it with:

```shell
python examples/qt_demo.py
```
