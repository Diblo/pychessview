# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Shared pytest configuration for pychessview.qt unit tests."""

from typing import cast

import pytest
from PySide6.QtWidgets import QApplication

pytest.importorskip("PySide6")


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    """Provide one QApplication for unit tests that exercise Qt objects.

    Qt widgets and painters require an application instance. The fixture reuses
    an existing instance when one is already present so tests do not create
    competing application lifetimes.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return cast(QApplication, app)
