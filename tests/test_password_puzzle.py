import pytest
from unittest.mock import MagicMock, patch

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scenes'))

with patch('matplotlib.pyplot.pause'), \
     patch('matplotlib.pyplot.draw'):
    from password_puzzle import PasswordPuzzleGame


# ── Helpers ────────────────────────────────────────────────────────────────────

def make_game(fig, ax, password="SECRET", max_attempts=3):
    with patch.object(PasswordPuzzleGame, '_draw'):
        return PasswordPuzzleGame(fig, ax, clues=["Clue 1"], password=password, max_attempts=max_attempts)


# ── Password check ─────────────────────────────────────────────────────────────

def test_correct_password_wins(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax, password="SECRET")
    game.current_guess = "SECRET"
    with patch.object(game, '_draw'):
        game._check_password()
    assert game.state == "win"


def test_correct_password_case_insensitive(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax, password="secret")   # stored as uppercase
    game.current_guess = "SECRET"
    with patch.object(game, '_draw'):
        game._check_password()
    assert game.state == "win"


def test_wrong_password_stays_playing(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax, password="SECRET", max_attempts=3)
    game.current_guess = "WRONG"
    with patch.object(game, '_draw'):
        game._check_password()
    assert game.state == "playing"
    assert game.attempts == 1


def test_wrong_password_clears_guess(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    game.current_guess = "WRONG"
    with patch.object(game, '_draw'):
        game._check_password()
    assert game.current_guess == ""


def test_max_attempts_triggers_lose(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax, password="SECRET", max_attempts=2)
    game.attempts      = 1
    game.current_guess = "WRONG"
    with patch.object(game, '_draw'):
        game._check_password()
    assert game.state == "lose"


def test_empty_guess_ignored(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    game.current_guess = ""
    with patch.object(game, '_draw'):
        game._check_password()
    assert game.attempts == 0
    assert game.state == "playing"


# ── Key input ──────────────────────────────────────────────────────────────────

def test_letter_key_appends_uppercase(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    event   = MagicMock()
    event.key = "a"
    with patch.object(game, '_draw'):
        game._handle_key(event)
    assert game.current_guess == "A"


def test_digit_key_appends(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    event   = MagicMock()
    event.key = "3"
    with patch.object(game, '_draw'):
        game._handle_key(event)
    assert game.current_guess == "3"


def test_backspace_removes_last_char(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    game.current_guess = "AB"
    event = MagicMock()
    event.key = "backspace"
    with patch.object(game, '_draw'):
        game._handle_key(event)
    assert game.current_guess == "A"


def test_backspace_on_empty_is_safe(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    event   = MagicMock()
    event.key = "backspace"
    with patch.object(game, '_draw'):
        game._handle_key(event)
    assert game.current_guess == ""


def test_max_guess_length_enforced(mock_fig_ax):
    fig, ax = mock_fig_ax
    game    = make_game(fig, ax)
    game.current_guess = "A" * 16   # at max
    event = MagicMock()
    event.key = "z"
    with patch.object(game, '_draw'):
        game._handle_key(event)
    assert len(game.current_guess) == 16


def test_input_ignored_when_not_playing(mock_fig_ax):
    fig, ax    = mock_fig_ax
    game       = make_game(fig, ax)
    game.state = "win"
    event      = MagicMock()
    event.key  = "a"
    with patch.object(game, '_draw'):
        game._handle_key(event)
    assert game.current_guess == ""
