import numpy as np
import pytest
from unittest.mock import MagicMock, patch

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scenes'))

with patch('matplotlib.pyplot.pause'), \
     patch('matplotlib.pyplot.draw'):
    from nine_puzzle import NinePuzzleGame, SOLVED_ORDER, GRID_SIZE


# ── Helpers ────────────────────────────────────────────────────────────────────

def make_game(fig, ax):
    with patch.object(NinePuzzleGame, '_draw'):
        return NinePuzzleGame(fig, ax)


def set_tiles(game, flat):
    """Set tiles from a flat list and update empty position."""
    game.tiles = np.array(flat).reshape((GRID_SIZE, GRID_SIZE))
    game.empty = tuple(np.argwhere(game.tiles == 0)[0])


# ── Solvability ────────────────────────────────────────────────────────────────

def test_solvable_puzzle_detected(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    solvable = np.array([1, 2, 3, 4, 5, 6, 7, 8, 0])
    assert game._is_solvable(solvable.reshape(3, 3))


def test_unsolvable_puzzle_detected(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    # Swap tiles 1 and 2 — creates an odd number of inversions
    unsolvable = np.array([2, 1, 3, 4, 5, 6, 7, 8, 0])
    assert not game._is_solvable(unsolvable.reshape(3, 3))


def test_generated_tiles_always_solvable(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    for _ in range(20):
        tiles = game._generate_solvable_tiles()
        assert game._is_solvable(tiles)


# ── Adjacency ──────────────────────────────────────────────────────────────────

def test_adjacent_left_is_valid(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    set_tiles(game, [1, 2, 3, 4, 0, 5, 6, 7, 8])   # empty at (1,1)
    assert game._is_adjacent_to_empty(1, 0)          # left neighbour


def test_adjacent_right_is_valid(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    set_tiles(game, [1, 2, 3, 4, 0, 5, 6, 7, 8])
    assert game._is_adjacent_to_empty(1, 2)


def test_adjacent_above_is_valid(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    set_tiles(game, [1, 2, 3, 4, 0, 5, 6, 7, 8])
    assert game._is_adjacent_to_empty(0, 1)


def test_diagonal_not_adjacent(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    set_tiles(game, [1, 2, 3, 4, 0, 5, 6, 7, 8])
    assert not game._is_adjacent_to_empty(0, 0)   # diagonal


def test_non_neighbour_not_adjacent(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    set_tiles(game, [1, 2, 3, 4, 0, 5, 6, 7, 8])
    assert not game._is_adjacent_to_empty(2, 2)


# ── Move tile ──────────────────────────────────────────────────────────────────

def test_move_tile_swaps_correctly(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    set_tiles(game, [1, 2, 3, 4, 0, 5, 6, 7, 8])   # empty at (1,1)
    with patch.object(game, '_draw'):
        game._move_tile(1, 0)                         # move tile at (1,0)
    assert game.tiles[1, 1] == 4
    assert game.tiles[1, 0] == 0
    assert game.empty == (1, 0)


def test_move_increments_counter(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    set_tiles(game, [1, 2, 3, 4, 0, 5, 6, 7, 8])
    with patch.object(game, '_draw'):
        game._move_tile(1, 0)
    assert game.moves == 1


# ── Win condition ──────────────────────────────────────────────────────────────

def test_check_solved_correct(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    set_tiles(game, [1, 2, 3, 4, 5, 6, 7, 8, 0])
    game._check_solved()
    assert game.solved


def test_check_solved_incorrect(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    set_tiles(game, [1, 2, 3, 4, 5, 6, 7, 0, 8])   # 8 and 0 swapped
    game._check_solved()
    assert not game.solved


def test_full_solve_sequence(mock_fig_ax):
    """Move tiles into solved state via _move_tile and confirm win."""
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    # Set up one move away from solved
    set_tiles(game, [1, 2, 3, 4, 5, 6, 7, 0, 8])   # 0 at (2,1), 8 at (2,2)
    with patch.object(game, '_draw'):
        game._move_tile(2, 2)
    assert game.solved
