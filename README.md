# Pychessview

Pychessview is a Python library for building interactive chessboard UIs
without coupling presentation logic to a specific GUI framework or chess engine.

The project is published as a single PyPI distribution:

- `pychessview`: core package providing board state, layout, rendering,
  interaction handling, themes, and the public view API
- `pychessview.qt`: optional Qt integration module enabled through the `qt` extra

## Requirements

- Python 3.11 or newer
- Core runtime dependencies installed automatically with `pychessview`
- For Qt widget support, `PySide6` is required

Install only the core package when no GUI backend is needed:

```shell
pip install pychessview
```

Install the optional Qt widget support when using PySide:

```shell
pip install "pychessview[qt]"
```

The core package defines rendering contracts, game/session orchestration,
and interaction behavior while remaining backend-agnostic. The optional Qt
module builds on this foundation with `QtRenderer`, `QtControllerAdapter`, and
`ChessboardWidget`.

This design enables reusable and extensible chessboard UIs for applications such
as chess GUIs, analysis tools, and training software, where the UI layer remains
independent from the underlying game implementation.

## Quick Start

Qt provides the simplest way to render a chessboard:

```python
from PySide6.QtWidgets import QApplication

from pychessview import StandardChessFactory
from pychessview.qt import ChessboardWidget


def main() -> int:
    app = QApplication.instance() or QApplication([])

    widget = ChessboardWidget(game_spec=StandardChessFactory.create_game_spec())
    widget.resize(640, 640)
    widget.show()

    return app.exec()
```

The core package can also be used without Qt by providing a
`pychessview.RendererProtocol` implementation and initializing `pychessview.View`
directly.

## Documentation

- [Engine Guide](https://github.com/Diblo/pychessview/blob/main/docs/engine.md): backend-agnostic engine usage
  with `View`, `GameSpec`, themes, and renderers
- [Qt Widget Guide](https://github.com/Diblo/pychessview/blob/main/docs/qt_widget.md): widget construction,
  state access, and Qt-specific behavior
- [Development Guide](https://github.com/Diblo/pychessview/blob/main/docs/development.md): workspace layout,
  architecture, tooling, and test conventions

## Example

A runnable Qt example is available at
[examples/qt_demo.py](https://github.com/Diblo/pychessview/blob/main/examples/qt_demo.py).

![Chessboard preview](https://media.githubusercontent.com/media/Diblo/pychessview/refs/heads/main/docs/assets/chessboard_preview.png)

The Qt example supports these interactions:

- Use the left mouse button to select, move, and drag pieces.
- Use Shift, Ctrl, or Alt with the left mouse button to add a circle or arrow.
- Use the right mouse button to delete a circle or arrow.

## License

This project is licensed under the Apache License 2.0.

GitHub profile: [Diblo/pychessview](https://github.com/Diblo/pychessview)
