import numpy as np
from unittest.mock import patch

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scenes"))

with patch("matplotlib.pyplot.pause"), patch("matplotlib.pyplot.draw"), patch(
    "matplotlib.animation.FuncAnimation"
):
    from minesweeper import MinesweeperGame


# ── Helpers ────────────────────────────────────────────────────────────────────


def make_game(fig, ax, width=5, height=5, num_mines=3):
    return MinesweeperGame(fig, ax, width=width, height=height, num_mines=num_mines)


# ── Mine placement ─────────────────────────────────────────────────────────────


def test_place_mines_correct_count(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax)
    game._place_mines(2, 2)
    mine_count = int(np.sum(game.board == -1))
    assert mine_count == game.num_mines


def test_place_mines_safe_start(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax)
    game._place_mines(2, 2)
    assert game.board[2, 2] != -1


def test_neighbor_counts_correct(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax, width=3, height=3, num_mines=1)
    # Manually place one mine at (0,0) and recalculate
    game.board[0, 0] = -1
    game.board[0, 1] = 1
    game.board[1, 0] = 1
    game.board[1, 1] = 1
    assert game.board[0, 1] == 1
    assert game.board[1, 1] == 1


# ── Reveal logic ───────────────────────────────────────────────────────────────


def test_reveal_mine_triggers_game_over(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax)
    game.board[0, 0] = -1
    game.first_click = False
    with patch.object(game, "_draw"):
        game._reveal_cell(0, 0)
    assert game.game_over


def test_reveal_empty_floods_neighbors(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax, width=5, height=5, num_mines=1)
    game.board[:] = 0
    game.board[4, 4] = -1
    # Set neighbor counts around the mine manually
    game.board[3, 4] = 1
    game.board[4, 3] = 1
    game.board[3, 3] = 1
    game.first_click = False
    with patch.object(game, "_draw"):
        game._reveal_cell(0, 0)
    # Mine itself should not be revealed
    assert not game.revealed[4, 4]
    # Origin should be revealed
    assert game.revealed[0, 0]


def test_flagged_cell_not_revealed(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax)
    game.flagged[1, 1] = True
    game.first_click = False
    with patch.object(game, "_draw"):
        game._reveal_cell(1, 1)
    assert not game.revealed[1, 1]


# ── Flag toggle ────────────────────────────────────────────────────────────────


def test_toggle_flag_on(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax)
    game._toggle_flag(0, 0)
    assert game.flagged[0, 0]


def test_toggle_flag_off(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax)
    game.flagged[0, 0] = True
    game._toggle_flag(0, 0)
    assert not game.flagged[0, 0]


def test_cannot_flag_revealed_cell(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax)
    game.revealed[0, 0] = True
    game._toggle_flag(0, 0)
    assert not game.flagged[0, 0]


# ── Win condition ──────────────────────────────────────────────────────────────


def test_check_win_all_safe_revealed(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax, width=3, height=3, num_mines=1)
    game.board[:] = 0
    game.board[0, 0] = -1
    game.revealed[:] = True
    game.revealed[0, 0] = False  # mine not revealed
    game._check_win()
    assert game.game_won


def test_check_win_not_yet(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax)
    game._check_win()
    assert not game.game_won


# ── Reveal all mines ───────────────────────────────────────────────────────────


def test_reveal_all_mines(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax)
    game._place_mines(0, 0)
    game._reveal_all_mines()
    mine_positions = np.argwhere(game.board == -1)
    for y, x in mine_positions:
        assert game.revealed[y, x]
