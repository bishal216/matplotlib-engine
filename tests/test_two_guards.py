import os
from unittest.mock import MagicMock, patch
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scenes"))

with patch("matplotlib.pyplot.pause"), patch("matplotlib.pyplot.draw"):
    from two_guards import TwoGuardsGame


# ── Helpers ────────────────────────────────────────────────────────────────────


def make_game(fig, ax, safe_door=1, truth_guard=1):
    with patch.object(TwoGuardsGame, "_draw"):
        game = TwoGuardsGame(fig, ax)
    game.safe_door = safe_door
    game.truth_guard = truth_guard
    game.liar_guard = 2 if truth_guard == 1 else 1
    return game


# ── Core riddle logic ──────────────────────────────────────────────────────────


def test_truth_guard_points_to_trap(mock_fig_ax):
    """Asking the truth-teller should always return the trap door."""
    fig, ax = mock_fig_ax
    game = make_game(fig, ax, safe_door=1, truth_guard=1)
    answer = game._guard_points_to(1)  # ask truth guard
    assert answer == 2  # should point to trap (door 2)


def test_liar_guard_also_points_to_trap(mock_fig_ax):
    """Asking the liar should also always return the trap door."""
    fig, ax = mock_fig_ax
    game = make_game(fig, ax, safe_door=1, truth_guard=1)
    answer = game._guard_points_to(2)  # ask liar guard
    assert answer == 2  # still points to trap


def test_both_guards_always_point_to_trap_door(mock_fig_ax):
    """Exhaustive check: regardless of config, both guards point to trap."""
    fig, ax = mock_fig_ax
    for safe_door in (1, 2):
        for truth_guard in (1, 2):
            game = make_game(fig, ax, safe_door=safe_door, truth_guard=truth_guard)
            trap = 2 if safe_door == 1 else 1
            assert game._guard_points_to(1) == trap
            assert game._guard_points_to(2) == trap


def test_optimal_strategy_always_wins(mock_fig_ax):
    """Player who always picks opposite of guard answer should always win."""
    fig, ax = mock_fig_ax
    for safe_door in (1, 2):
        for truth_guard in (1, 2):
            for asked_guard in (1, 2):
                game = make_game(fig, ax, safe_door=safe_door, truth_guard=truth_guard)
                game.state = "ask"
                with patch.object(game, "_draw"):
                    game._ask_guard(asked_guard)
                pointed_door = game.guard_answer
                opposite = 2 if pointed_door == 1 else 1
                with patch.object(game, "_draw"):
                    game._choose_door(opposite)
                assert (
                    game.state == "win"
                ), f"Failed: safe={safe_door} truth={truth_guard} asked={asked_guard}"


# ── State transitions ──────────────────────────────────────────────────────────


def test_initial_state_is_intro(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax)
    assert game.state == "intro"


def test_space_advances_to_ask(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax)
    event = MagicMock()
    event.key = " "
    with patch.object(game, "_draw"):
        game._on_key(event)
    assert game.state == "ask"


def test_ask_guard_advances_to_choose(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax)
    game.state = "ask"
    with patch.object(game, "_draw"):
        game._ask_guard(1)
    assert game.state == "choose"
    assert game.asked_guard == 1
    assert game.guard_answer in (1, 2)


def test_choose_correct_door_wins(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax, safe_door=2)
    game.state = "choose"
    with patch.object(game, "_draw"):
        game._choose_door(2)
    assert game.state == "win"


def test_choose_wrong_door_loses(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax, safe_door=2)
    game.state = "choose"
    with patch.object(game, "_draw"):
        game._choose_door(1)
    assert game.state == "lose"


def test_cannot_choose_during_intro(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax)
    with patch.object(game, "_draw"):
        game._choose_door(1)
    assert game.state == "intro"  # state unchanged


def test_cannot_ask_during_choose(mock_fig_ax):
    fig, ax = mock_fig_ax
    game = make_game(fig, ax)
    game.state = "choose"
    with patch.object(game, "_draw"):
        game._ask_guard(1)
    assert game.state == "choose"  # state unchanged
