import pytest
from unittest.mock import MagicMock, patch
import numpy as np

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scenes'))

with patch('matplotlib.pyplot.pause'), \
     patch('matplotlib.pyplot.draw'), \
     patch('matplotlib.animation.FuncAnimation'):
    from pong_game import PongGame, PADDLE_X, PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED, BALL_RADIUS, MAX_SPEED


# ── Helpers ────────────────────────────────────────────────────────────────────

def make_game(fig, ax):
    with patch.object(PongGame, '_draw'):
        return PongGame(fig, ax, width=10, height=8)


# ── Paddle movement ────────────────────────────────────────────────────────────

def test_paddle_moves_up_when_up_held(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    game._keys_held = {"up"}
    initial_y = game.paddle_y
    game._apply_paddle_input()
    assert game.paddle_y > initial_y


def test_paddle_moves_down_when_down_held(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    game._keys_held = {"down"}
    game.paddle_y   = 4.0
    initial_y       = game.paddle_y
    game._apply_paddle_input()
    assert game.paddle_y < initial_y


def test_paddle_clamped_at_top(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    game._keys_held = {"up"}
    game.paddle_y   = game.height - PADDLE_HEIGHT   # already at top
    game._apply_paddle_input()
    assert game.paddle_y <= game.height - PADDLE_HEIGHT


def test_paddle_clamped_at_bottom(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    game._keys_held = {"down"}
    game.paddle_y   = 0.0   # already at bottom
    game._apply_paddle_input()
    assert game.paddle_y >= 0


def test_paddle_stationary_with_no_keys(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    game._keys_held = set()
    initial_y       = game.paddle_y
    game._apply_paddle_input()
    assert game.paddle_y == initial_y


# ── Ball bouncing ──────────────────────────────────────────────────────────────

def test_ball_bounces_off_top_wall(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    game.ball_pos = [5.0, game.height - BALL_RADIUS + 0.1]
    game.ball_vel = [0.1, 0.1]   # moving up
    with patch.object(game, '_draw'):
        game._update(0)
    assert game.ball_vel[1] < 0   # now moving down


def test_ball_bounces_off_bottom_wall(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    game.ball_pos = [5.0, BALL_RADIUS - 0.1]
    game.ball_vel = [0.1, -0.1]   # moving down
    with patch.object(game, '_draw'):
        game._update(0)
    assert game.ball_vel[1] > 0   # now moving up


def test_ball_bounces_off_right_wall(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    game.ball_pos = [game.width - BALL_RADIUS + 0.1, 4.0]
    game.ball_vel = [0.1, 0.0]   # moving right
    with patch.object(game, '_draw'):
        game._update(0)
    assert game.ball_vel[0] < 0   # now moving left


# ── Paddle collision ───────────────────────────────────────────────────────────

def test_paddle_hit_increments_score(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    # Position ball overlapping paddle
    game.ball_pos = [PADDLE_X + PADDLE_WIDTH - BALL_RADIUS, game.paddle_y + PADDLE_HEIGHT / 2]
    game.ball_vel = [-0.15, 0.0]   # moving left into paddle
    with patch.object(game, '_draw'):
        game._update(0)
    assert game.score == 1
    assert game.ball_vel[0] > 0   # deflected right


def test_ball_miss_triggers_game_over(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    # Ball past paddle entirely
    game.ball_pos = [PADDLE_X - BALL_RADIUS - 0.5, 4.0]
    game.ball_vel = [-0.15, 0.0]
    with patch.object(game, '_draw'):
        game._update(0)
    assert game.game_over


# ── Speed cap ──────────────────────────────────────────────────────────────────

def test_ball_speed_never_exceeds_max(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    # Simulate many paddle hits
    game.ball_pos = [PADDLE_X + PADDLE_WIDTH - BALL_RADIUS, game.paddle_y + PADDLE_HEIGHT / 2]
    game.ball_vel = [-0.15, 0.0]
    for _ in range(50):
        game.ball_pos[0] = PADDLE_X + PADDLE_WIDTH - BALL_RADIUS
        game.ball_vel[0] = -abs(game.ball_vel[0])
        with patch.object(game, '_draw'):
            game._update(0)
        speed = float(np.hypot(*game.ball_vel))
        assert speed <= MAX_SPEED + 0.01   # small float tolerance


# ── Key handling ───────────────────────────────────────────────────────────────

def test_key_press_adds_to_held(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    event   = MagicMock()
    event.key = "up"
    game._on_key_press(event)
    assert "up" in game._keys_held


def test_key_release_removes_from_held(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    game._keys_held = {"up"}
    event = MagicMock()
    event.key = "up"
    game._on_key_release(event)
    assert "up" not in game._keys_held
