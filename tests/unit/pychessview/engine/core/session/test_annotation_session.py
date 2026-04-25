# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for annotation session behavior."""

import pytest

from pychessview.engine.core.annotation_types import ArrowType, CircleType, HintArrowType
from pychessview.engine.core.exceptions import ChessboardViewError
from pychessview.engine.core.primitives import Move, PlayerColor, Square
from pychessview.engine.core.session.annotation_session import AnnotationSession
from pychessview.engine.core.state.annotation_state import AnnotationState
from pychessview.engine.core.state.promotion_state import PromotionState

pytestmark = pytest.mark.unit


def test_annotation_session_writes_previews_and_persistent_annotations() -> None:
    """Coordinate annotation state updates without changing unrelated annotation groups."""
    annotation_state = AnnotationState()
    session = AnnotationSession.create(annotation_state, PromotionState((), ()))
    origin = Square(0, 0)
    target = Square(1, 0)

    session.set_circle_preview(CircleType.PRIMARY, origin)
    assert annotation_state.get_circle_preview() == (CircleType.PRIMARY, origin)

    session.set_arrow_preview(ArrowType.SECONDARY, origin, target, has_corner=True)
    assert annotation_state.get_circle_preview() is None
    assert annotation_state.get_arrow_preview() == (ArrowType.SECONDARY, (origin, target, True))

    session.add_circle(CircleType.ALTERNATIVE, origin)
    session.add_arrow(ArrowType.PRIMARY, origin, target)
    session.add_hint_arrow(HintArrowType.PRIMARY, target, origin)

    assert annotation_state.get_circles() == ((CircleType.ALTERNATIVE, origin),)
    assert annotation_state.get_arrows() == ((ArrowType.PRIMARY, (origin, target), False),)
    assert annotation_state.get_hint_arrows() == ((HintArrowType.PRIMARY, (target, origin), False),)


def test_annotation_session_remove_methods_only_clear_matching_annotation_groups() -> None:
    """Remove user annotations without touching hint arrows or unrelated stored annotations."""
    annotation_state = AnnotationState()
    session = AnnotationSession(annotation_state, PromotionState((), ()))
    origin = Square(0, 0)
    target = Square(1, 0)

    session.add_circle(CircleType.PRIMARY, origin)
    session.add_circle(CircleType.SECONDARY, target)
    session.add_arrow(ArrowType.PRIMARY, origin, target)
    session.add_hint_arrow(HintArrowType.PRIMARY, origin, target)

    session.remove_circle(origin)
    session.remove_arrow(origin, target)

    assert annotation_state.get_circles() == ((CircleType.SECONDARY, target),)
    assert annotation_state.get_arrows() == ()
    assert annotation_state.get_hint_arrows() == ((HintArrowType.PRIMARY, (origin, target), False),)


def test_annotation_session_rejects_mutation_while_promotion_is_active() -> None:
    """Block annotation edits during promotion selection so promotion UI state remains authoritative."""
    promotion_state = PromotionState((), ())
    promotion_state.show_promotion(Move(Square(0, 6), Square(0, 7)), PlayerColor.WHITE)
    annotation_state = AnnotationState()
    session = AnnotationSession(annotation_state, promotion_state)

    with pytest.raises(ChessboardViewError, match="promotion is active"):
        session.add_circle(CircleType.PRIMARY, Square(0, 0))

    assert annotation_state.has_annotation() is False


def test_annotation_session_clear_methods_remain_available_for_cleanup() -> None:
    """Allow cleanup paths to clear annotation state without being blocked by existing annotation content."""
    annotation_state = AnnotationState()
    session = AnnotationSession(annotation_state, PromotionState((), ()))
    origin = Square(0, 0)
    target = Square(1, 0)

    session.set_circle_preview(CircleType.PRIMARY, origin)
    session.add_circle(CircleType.PRIMARY, origin)
    session.add_arrow(ArrowType.PRIMARY, origin, target)
    session.add_hint_arrow(HintArrowType.PRIMARY, origin, target)

    session.clear_preview()
    session.clear_circles()
    session.clear_arrows()
    session.clear_hint_arrows()

    assert annotation_state.has_annotation() is False
