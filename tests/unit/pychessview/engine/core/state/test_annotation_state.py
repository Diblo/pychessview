# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for annotation state."""

import pytest

from pychessview.engine.core.annotation_types import ArrowType, CircleType, HintArrowType
from pychessview.engine.core.primitives import File, Rank, Square
from pychessview.engine.core.state.annotation_state import AnnotationState

pytestmark = pytest.mark.unit


def test_annotation_state_keeps_previews_mutually_exclusive() -> None:
    """Store only one active annotation preview at a time.

    Circle and arrow previews represent different interaction modes. Setting
    one must clear the other so render layers never show stale preview state.
    """
    state = AnnotationState()
    from_square = Square(File.A, Rank.ONE)
    to_square = Square(File.H, Rank.EIGHT)

    state.set_circle_preview(CircleType.PRIMARY, from_square)
    assert state.get_circle_preview() == (CircleType.PRIMARY, from_square)
    assert state.get_arrow_preview() is None
    assert state.has_preview() is True

    state.set_arrow_preview(ArrowType.SECONDARY, from_square, to_square, True)
    assert state.get_circle_preview() is None
    assert state.get_arrow_preview() == (ArrowType.SECONDARY, (from_square, to_square, True))

    state.clear_preview()
    assert state.has_preview() is False


def test_annotation_state_tracks_user_circles_arrows_and_hint_arrows_separately() -> None:
    """Keep user annotations and hint arrows in separate storage groups.

    Annotation deletion and hint rendering have different lifecycles. Removing a
    user annotation must not remove engine-provided hint arrows.
    """
    state = AnnotationState()
    from_square = Square(File.B, Rank.TWO)
    to_square = Square(File.C, Rank.THREE)

    state.add_circle(CircleType.ALTERNATIVE, from_square)
    state.add_arrow(ArrowType.PRIMARY, from_square, to_square, False)
    state.add_hint_arrow(HintArrowType.SECONDARY, from_square, to_square, True)

    assert state.get_circles() == ((CircleType.ALTERNATIVE, from_square),)
    assert state.get_arrows() == ((ArrowType.PRIMARY, (from_square, to_square), False),)
    assert state.get_hint_arrows() == ((HintArrowType.SECONDARY, (from_square, to_square), True),)
    assert state.has_annotation() is True

    state.remove_circle(from_square)
    state.remove_arrow(from_square, to_square)
    assert state.get_hint_arrows() == ((HintArrowType.SECONDARY, (from_square, to_square), True),)


def test_annotation_state_clear_all_removes_every_annotation_group() -> None:
    """Clear previews, user annotations, and hint arrows together.

    Loading a new game or clearing the board needs one operation that returns
    annotation state to an empty baseline.
    """
    state = AnnotationState()
    from_square = Square(File.D, Rank.FOUR)
    to_square = Square(File.E, Rank.FIVE)

    state.set_circle_preview(CircleType.PRIMARY, from_square)
    state.add_circle(CircleType.PRIMARY, from_square)
    state.add_arrow(ArrowType.PRIMARY, from_square, to_square)
    state.add_hint_arrow(HintArrowType.PRIMARY, from_square, to_square)

    state.clear_all()

    assert state.get_circle_preview() is None
    assert state.get_arrow_preview() is None
    assert state.get_circles() == ()
    assert state.get_arrows() == ()
    assert state.get_hint_arrows() == ()
    assert state.has_annotation() is False


def test_annotation_state_missing_removals_are_no_ops() -> None:
    """Ignore removal requests for annotations that are not present.

    Controller deletion can call remove methods without querying first; missing
    user annotations must leave existing circles, arrows, and hint arrows intact.
    """
    state = AnnotationState()
    circle_square = Square(File.A, Rank.ONE)
    arrow_from = Square(File.B, Rank.TWO)
    arrow_to = Square(File.C, Rank.THREE)

    state.add_circle(CircleType.PRIMARY, circle_square)
    state.add_arrow(ArrowType.PRIMARY, arrow_from, arrow_to)
    state.add_hint_arrow(HintArrowType.PRIMARY, arrow_from, arrow_to)

    state.remove_circle(Square(File.H, Rank.EIGHT))
    state.remove_arrow(Square(File.D, Rank.FOUR), Square(File.E, Rank.FIVE))
    state.remove_hint_arrow(Square(File.F, Rank.SIX), Square(File.G, Rank.SEVEN))

    assert state.get_circles() == ((CircleType.PRIMARY, circle_square),)
    assert state.get_arrows() == ((ArrowType.PRIMARY, (arrow_from, arrow_to), False),)
    assert state.get_hint_arrows() == ((HintArrowType.PRIMARY, (arrow_from, arrow_to), False),)
