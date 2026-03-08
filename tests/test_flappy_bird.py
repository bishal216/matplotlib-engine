import pytest
from unittest.mock import MagicMock, patch

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scenes'))

with patch('matplotlib.pyplot.pause'), \
     patch('matplotlib.pyplot.draw'), \
     patch('matplotlib.animation.FuncAnimation'):
    from flappy_bird import FlappyBirdGame, GRAVITY, FLAP_STRENGTH, BIRD_X, BIRD_RADIUS, PIPE_GAP, PIPE_WIDTH


# ── Helpers ────────────────────────────────────────────────────────────────────

def make_game(fig, ax, score_to_beat=5):
    with patch.object(FlappyBirdGame, '_draw'):
        return FlappyBirdGame(fig, ax, score_to_beat=score_to_beat, width=10, height=8)


# ── Physics ────────────────────────────────────────────────────────────────────

def test_gravity_pulls_bird_down(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    game.started = True
    initial_y    = game.bird_y
    with patch.object(game, '_draw'):
        game._update(0)
    assert game.bird_y < initial_y or game.bird_vy < 0


def test_flap_sets_upward_velocity(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    game.started  = True
    game.bird_vy  = -0.2   # falling
    game._flap()
    assert game.bird_vy == FLAP_STRENGTH


def test_flap_ignored_when_game_over(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    game.game_over = True
    game.bird_vy   = -0.2
    game._flap()
    assert game.bird_vy == -0.2   # unchanged


# ── Boundary collision ─────────────────────────────────────────────────────────

def test_floor_collision_triggers_game_over(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    game.started  = True
    game.bird_y   = BIRD_RADIUS - 0.1   # below floor
    game.bird_vy  = -1.0
    with patch.object(game, '_draw'):
        game._update(0)
    assert game.game_over


def test_ceiling_collision_triggers_game_over(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    game.started  = True
    game.bird_y   = game.height - BIRD_RADIUS + 0.1   # above ceiling
    game.bird_vy  = 1.0
    with patch.object(game, '_draw'):
        game._update(0)
    assert game.game_over


# ── Pipe collision ─────────────────────────────────────────────────────────────

def test_pipe_collision_below_gap(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    game.started = True
    game.pipes   = [{"x": BIRD_X - BIRD_RADIUS, "gap_y": 4.0}]
    game.bird_y  = 2.0   # below gap (gap starts at 4.0)
    game.bird_vy = 0.0
    with patch.object(game, '_draw'):
        game._update(0)
    assert game.game_over


def test_pipe_no_collision_inside_gap(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    game.started = True
    game.pipes   = [{"x": BIRD_X - BIRD_RADIUS, "gap_y": 2.0}]
    game.bird_y  = 2.0 + PIPE_GAP / 2   # inside gap
    game.bird_vy = 0.0
    with patch.object(game, '_draw'):
        game._update(0)
    assert not game.game_over


# ── Scoring ────────────────────────────────────────────────────────────────────

def test_score_increments_on_pipe_pass(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    game.started = True
    # Place pipe just behind the left edge so it gets popped next update
    game.pipes   = [{"x": -PIPE_WIDTH - 0.1, "gap_y": 3.0}]
    game.bird_y  = 4.0
    game.bird_vy = 0.0
    with patch.object(game, '_draw'):
        game._update(0)
    assert game.score == 1


def test_win_when_score_reaches_target(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax, score_to_beat=3)
    game.score     = 3
    game.started   = True
    game.bird_y    = 4.0
    game.bird_vy   = 0.0
    game.pipes     = []
    with patch.object(game, '_draw'):
        game._update(0)
    assert game.game_over


# ── Pipe spawning ──────────────────────────────────────────────────────────────

def test_spawn_pipe_adds_to_list(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    game.pipes = []
    game._spawn_pipe()
    assert len(game.pipes) == 1
    assert game.pipes[0]["x"] == game.width


def test_spawn_pipe_gap_within_bounds(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    for _ in range(50):
        game.pipes = []
        game._spawn_pipe()
        gap_y = game.pipes[0]["gap_y"]
        assert gap_y + PIPE_GAP <= game.height
        assert gap_y >= 0
