import numpy as np
import pytest
from unittest.mock import MagicMock, patch

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scenes'))

with patch('matplotlib.pyplot.pause'), \
     patch('matplotlib.pyplot.draw'), \
     patch('matplotlib.animation.FuncAnimation'):
    from tetris_game import TetrisGame, PIECES, COLOR_INDEX, DROP_FRAMES_INIT, DROP_FRAMES_MIN, DROP_SPEED_EVERY


# ── Helpers ────────────────────────────────────────────────────────────────────

def make_game(fig, ax):
    with patch.object(TetrisGame, '_draw'):
        return TetrisGame(fig, ax, width=10, height=20)


def set_piece(game, name, x, y):
    game.current_piece = PIECES[name]["shape"].copy()
    game.current_color = name
    game.current_x     = x
    game.current_y     = y


# ── Validity checks ────────────────────────────────────────────────────────────

def test_valid_position_empty_board(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    piece   = PIECES["O"]["shape"]
    assert game._is_valid(piece, 4, 18)


def test_invalid_position_out_of_bounds_left(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    piece   = PIECES["I"]["shape"]
    assert not game._is_valid(piece, -1, 10)


def test_invalid_position_out_of_bounds_bottom(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    piece   = PIECES["O"]["shape"]
    assert not game._is_valid(piece, 4, 0)


def test_invalid_position_collision_with_board(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    piece   = PIECES["O"]["shape"]
    game.board[1, 4] = 1
    assert not game._is_valid(piece, 4, 1)


# ── Piece placement ────────────────────────────────────────────────────────────

def test_place_piece_stores_colour(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    set_piece(game, "O", 4, 1)
    game._place_piece()
    expected_idx = COLOR_INDEX["O"]
    assert game.board[1, 4] == expected_idx
    assert game.board[1, 5] == expected_idx
    assert game.board[0, 4] == expected_idx
    assert game.board[0, 5] == expected_idx


def test_place_piece_i_horizontal(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    set_piece(game, "I", 3, 0)
    game._place_piece()
    expected_idx = COLOR_INDEX["I"]
    for col in range(3, 7):
        assert game.board[0, col] == expected_idx


# ── Line clearing ──────────────────────────────────────────────────────────────

def test_clear_one_line(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    game.board[0, :] = 1   # fill bottom row
    game._clear_lines()
    assert game.lines_cleared == 1
    assert game.score == 100


def test_clear_two_lines_bonus_score(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    game.board[0, :] = 1
    game.board[1, :] = 1
    game._clear_lines()
    assert game.lines_cleared == 2
    assert game.score == 400   # 2 * 2 * 100


def test_clear_lines_shifts_board_down(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    game.board[0, :] = 1    # full row at y=0
    game.board[1, 0] = 2    # marker above cleared row
    game._clear_lines()
    # Row 0 was cleared, row 1 shifts down to row 0
    assert game.board[0, 0] == 2
    # Top row should now be empty
    assert game.board[game.height - 1, :].sum() == 0


def test_no_lines_cleared(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    game.board[0, 0] = 1    # partial row — not full
    game._clear_lines()
    assert game.lines_cleared == 0
    assert game.score == 0


# ── Speed scaling ──────────────────────────────────────────────────────────────

def test_speed_increases_with_lines(mock_fig_ax):
    fig, ax  = mock_fig_ax
    game     = make_game(fig, ax)
    initial  = game._drop_frames
    game.lines_cleared = DROP_SPEED_EVERY
    game.board[0, :]   = 1
    game._clear_lines()
    assert game._drop_frames < initial


def test_speed_never_below_minimum(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    game.lines_cleared = DROP_SPEED_EVERY * 100   # very high level
    game.board[0, :]   = 1
    game._clear_lines()
    assert game._drop_frames >= DROP_FRAMES_MIN


# ── Ghost piece ────────────────────────────────────────────────────────────────

def test_ghost_y_lands_at_bottom(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    set_piece(game, "O", 4, 18)
    ghost   = game._ghost_y()
    # O piece has shape height 2, so minimum valid y is 1 (occupies rows 0 and 1)
    assert ghost == 1


def test_ghost_y_blocked_by_board(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    set_piece(game, "O", 4, 10)
    # O piece has height=2: occupies rows [current_y, current_y-1]
    # Block at y=5 means piece bottom (current_y - 1) can reach y=6, so current_y=7
    game.board[5, 4] = 1
    ghost = game._ghost_y()
    assert ghost == 7


# ── Hard drop ──────────────────────────────────────────────────────────────────

def test_hard_drop_lands_piece(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    set_piece(game, "O", 4, 10)
    with patch.object(game, '_draw'):
        game._hard_drop()
    # After hard drop a new piece spawns — board bottom rows should be filled
    expected_idx = COLOR_INDEX["O"]
    assert game.board[0, 4] == expected_idx or game.board[0, 5] == expected_idx


def test_hard_drop_awards_bonus(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    set_piece(game, "O", 4, 10)
    with patch.object(game, '_draw'):
        game._hard_drop()
    assert game.score > 0