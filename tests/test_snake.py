import pytest
from unittest.mock import MagicMock, patch
from collections import deque

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scenes'))

with patch('matplotlib.pyplot.pause'), \
     patch('matplotlib.pyplot.draw'), \
     patch('matplotlib.animation.FuncAnimation'):
    from snake_game import SnakeGame, DIR_LEFT, DIR_RIGHT, DIR_UP, DIR_DOWN


# ── Helpers ────────────────────────────────────────────────────────────────────

def make_game(fig, ax, width=10, height=10):
    return SnakeGame(fig, ax, width=width, height=height)


def set_snake(game, positions):
    """Helper to set snake to a specific set of positions."""
    game.snake     = deque(positions)
    game.snake_set = set(positions)


# ── Movement ───────────────────────────────────────────────────────────────────

def test_snake_moves_right(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax)
    set_snake(game, [(5, 5)])
    game.direction   = DIR_RIGHT
    game._queued_dir = DIR_RIGHT
    with patch.object(game, '_draw'):
        game._move_snake()
    assert game.snake[0] == (6, 5)


def test_snake_moves_up(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax)
    set_snake(game, [(5, 5)])
    game.direction   = DIR_UP
    game._queued_dir = DIR_UP
    with patch.object(game, '_draw'):
        game._move_snake()
    assert game.snake[0] == (5, 6)


# ── Wall collision ─────────────────────────────────────────────────────────────

def test_wall_collision_left(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax)
    set_snake(game, [(0, 5)])
    game.direction   = DIR_LEFT
    game._queued_dir = DIR_LEFT
    with patch.object(game, '_draw'):
        game._move_snake()
    assert game.game_over


def test_wall_collision_right(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax, width=10)
    set_snake(game, [(9, 5)])
    game.direction   = DIR_RIGHT
    game._queued_dir = DIR_RIGHT
    with patch.object(game, '_draw'):
        game._move_snake()
    assert game.game_over


def test_wall_collision_top(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax, height=10)
    set_snake(game, [(5, 9)])
    game.direction   = DIR_UP
    game._queued_dir = DIR_UP
    with patch.object(game, '_draw'):
        game._move_snake()
    assert game.game_over


def test_wall_collision_bottom(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax)
    set_snake(game, [(5, 0)])
    game.direction   = DIR_DOWN
    game._queued_dir = DIR_DOWN
    with patch.object(game, '_draw'):
        game._move_snake()
    assert game.game_over


# ── Self collision ─────────────────────────────────────────────────────────────

def test_self_collision(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax)
    # Snake curled so head will move into body
    set_snake(game, [(5, 5), (6, 5), (6, 6), (5, 6)])
    game.direction   = DIR_UP
    game._queued_dir = DIR_UP
    with patch.object(game, '_draw'):
        game._move_snake()
    assert game.game_over


# ── Food ───────────────────────────────────────────────────────────────────────

def test_eating_food_grows_snake(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax)
    set_snake(game, [(5, 5)])
    game.direction   = DIR_RIGHT
    game._queued_dir = DIR_RIGHT
    game.food        = (6, 5)   # food right in front
    with patch.object(game, '_draw'):
        game._move_snake()
    assert len(game.snake) == 2
    assert game.score == 10


def test_not_eating_food_stays_same_length(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax)
    set_snake(game, [(5, 5), (4, 5)])
    game.direction   = DIR_RIGHT
    game._queued_dir = DIR_RIGHT
    game.food        = (9, 9)   # food far away
    with patch.object(game, '_draw'):
        game._move_snake()
    assert len(game.snake) == 2


def test_food_not_placed_on_snake(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax, width=5, height=5)
    # Fill almost entire board with snake
    positions = [(x, y) for x in range(5) for y in range(5) if not (x == 4 and y == 4)]
    set_snake(game, positions)
    food = game._generate_food()
    assert food not in game.snake_set


# ── Direction buffering ────────────────────────────────────────────────────────

def test_cannot_reverse_direction(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax)
    game.direction = DIR_RIGHT
    # Simulate pressing left (opposite)
    event = MagicMock()
    event.key = "left"
    game._on_key(event)
    assert game._queued_dir == DIR_RIGHT   # direction unchanged


def test_valid_direction_change(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax)
    game.direction = DIR_RIGHT
    event = MagicMock()
    event.key = "up"
    game._on_key(event)
    assert game._queued_dir == DIR_UP
