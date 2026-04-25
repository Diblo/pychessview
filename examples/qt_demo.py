# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Qt demo for the optional pychessview.qt widget package."""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

# Allow running this file directly from the source tree.
SRC_DIR = str(Path(__file__).resolve().parents[1] / "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from pychessview import StandardChessFactory  # noqa: E402
from pychessview.qt import ChessboardWidget  # noqa: E402


def main() -> int:
    """Run the Qt demo application.

    Returns:
        Exit status returned by ``app.exec()``.
    """
    app = QApplication.instance() or QApplication([])

    widget = ChessboardWidget(game_spec=StandardChessFactory.create_game_spec())

    widget.setWindowTitle("ChessboardWidget Qt Demo")
    widget.resize(640, 640)

    widget.settings.restrict_to_player_pieces = False

    widget.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
