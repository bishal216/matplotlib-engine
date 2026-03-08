import os
from unittest.mock import MagicMock, patch

import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

with patch("matplotlib.pyplot.ion"), patch("matplotlib.pyplot.subplots"), patch(
    "matplotlib.pyplot.pause"
), patch("matplotlib.pyplot.draw"):
    from game import SceneManager


# ── Helpers ────────────────────────────────────────────────────────────────────

CHARACTERS = {
    "Alice": {"sprite": None, "side": "left"},
    "Bob": {"sprite": None, "side": "right"},
}

SETTINGS = {
    "forest": {"background": None},
}


def make_manager(scenes):
    return SceneManager(scenes, CHARACTERS, SETTINGS)


# ── Navigation ─────────────────────────────────────────────────────────────────


def test_has_next_when_scenes_remain(mock_fig_ax):
    manager = make_manager([{"type": "text"}])
    assert manager.has_next


def test_no_next_when_empty(mock_fig_ax):
    manager = make_manager([])
    assert not manager.has_next


def test_next_returns_scene_and_advances(mock_fig_ax):
    scenes = [{"type": "text", "title": "A"}, {"type": "text", "title": "B"}]
    manager = make_manager(scenes)
    scene = manager.next()
    assert scene["title"] == "A"
    assert manager.index == 1


def test_has_next_false_after_all_consumed(mock_fig_ax):
    manager = make_manager([{"type": "text"}])
    manager.next()
    assert not manager.has_next


# ── Scene rendering ────────────────────────────────────────────────────────────


def test_exit_scene_returns_false(mock_fig_ax):
    fig, ax = mock_fig_ax
    manager = make_manager([])
    result = manager.render({"type": "exit"}, fig, ax)
    assert result is False


def test_unknown_scene_type_returns_true(mock_fig_ax):
    fig, ax = mock_fig_ax
    manager = make_manager([])
    result = manager.render({"type": "unknown_type"}, fig, ax)
    assert result is True


def test_text_scene_calls_renderer(mock_fig_ax):
    fig, ax = mock_fig_ax
    manager = make_manager([])
    with patch("game.text_scene") as mock_text:
        manager.render({"type": "text"}, fig, ax)
    mock_text.assert_called_once()


def test_conversation_scene_calls_renderer(mock_fig_ax):
    fig, ax = mock_fig_ax
    manager = make_manager([])
    scene = {"type": "conversation", "location": "forest", "conversation": []}
    with patch("game.conversation_cutscene") as mock_conv:
        manager.render(scene, fig, ax)
    mock_conv.assert_called_once()


def test_unknown_minigame_skipped_gracefully(mock_fig_ax):
    fig, ax = mock_fig_ax
    manager = make_manager([])
    scene = {"type": "minigame", "game": "nonexistent_game"}
    # Should not raise
    result = manager.render(scene, fig, ax)
    assert result is True


def test_known_minigame_instantiated(mock_fig_ax):
    fig, ax = mock_fig_ax
    manager = make_manager([])
    mock_cls = MagicMock()
    mock_cls.return_value.run.return_value = None

    scene = {"type": "minigame", "game": "snake_game"}
    with patch.dict("game.MINIGAME_REGISTRY", {"snake_game": mock_cls}):
        manager.render(scene, fig, ax)

    mock_cls.assert_called_once()
    mock_cls.return_value.run.assert_called_once()


# ── Scene list normalisation ───────────────────────────────────────────────────


def test_scenes_dict_converted_to_list():
    scenes_dict = {"a": {"type": "text"}, "b": {"type": "exit"}}
    # Simulate what Game._load_story does
    scenes = (
        list(scenes_dict.values()) if isinstance(scenes_dict, dict) else scenes_dict
    )
    manager = make_manager(scenes)
    assert len(manager.scenes) == 2
    assert manager.has_next
