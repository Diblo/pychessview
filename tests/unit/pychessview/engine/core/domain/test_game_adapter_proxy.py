# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for game adapter proxy delegation."""

from __future__ import annotations

import pytest

from pychessview.engine.core.domain.game_adapter_proxy import GameAdapterProxy
from pychessview.engine.core.primitives import Move, Piece, PieceKind, PlayerColor, Square

from ..._helpers import GameAdapterProxyAdapterSpy

pytestmark = pytest.mark.unit


def test_game_adapter_proxy_delegates_properties_to_active_adapter() -> None:
    """Expose adapter properties through the proxy without caching stale values."""
    first = GameAdapterProxyAdapterSpy("first")
    second = GameAdapterProxyAdapterSpy("second")
    proxy = GameAdapterProxy(first)

    proxy.default_fen = "updated default"
    proxy.fen = "updated fen"
    proxy.switch_adapter(second)

    assert first.default_fen == "updated default"
    assert first.fen == "updated fen"
    assert proxy.default_fen == "second default"
    assert proxy.fen == "second fen"
    assert proxy.turn is PlayerColor.WHITE
    assert proxy.move_history == second.move_history


def test_game_adapter_proxy_forwards_board_state_operations() -> None:
    """Delegate board queries and mutations to the active adapter with exact payloads."""
    adapter = GameAdapterProxyAdapterSpy("active")
    proxy = GameAdapterProxy(adapter)
    origin = Square(0, 0)
    target = Square(1, 0)
    move = Move(origin, target)
    piece = Piece(PlayerColor.WHITE, PieceKind.QUEEN)

    assert proxy.pieces() == adapter.placement
    assert proxy.piece_at(origin) == Piece(PlayerColor.WHITE, PieceKind.KING)
    proxy.set_piece(target, piece)
    assert proxy.king(PlayerColor.BLACK) == adapter.king_square
    assert proxy.is_legal_move(move) is True
    assert proxy.is_promotion_move(move) is False
    assert proxy.has_move_history() is True
    proxy.move(move)
    assert proxy.is_check() is False
    assert proxy.is_checkmate() is False
    assert proxy.get_legal_hints(origin) == {Square(1, 0)}
    assert proxy.get_pseudo_legal_hints(origin, PlayerColor.WHITE) == {Square(2, 0)}
    assert adapter.calls == [
        ("pieces", ()),
        ("piece_at", origin),
        ("set_piece", (target, piece)),
        ("king", PlayerColor.BLACK),
        ("is_legal_move", move),
        ("is_promotion_move", move),
        ("has_move_history", ()),
        ("move", move),
        ("is_check", ()),
        ("is_checkmate", ()),
        ("get_legal_hints", origin),
        ("get_pseudo_legal_hints", (origin, PlayerColor.WHITE)),
    ]
