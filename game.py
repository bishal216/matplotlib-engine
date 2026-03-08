import matplotlib.pyplot as plt
import sys
import os
import json
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scenes.conversation_cutscene import conversation_cutscene
from scenes.text_scene import text_scene
from scenes.flappy_bird import FlappyBirdGame
from scenes.minesweeper import MinesweeperGame
from scenes.nine_puzzle import NinePuzzleGame
from scenes.password_puzzle import PasswordPuzzleGame
from scenes.pong_game import PongGame
from scenes.snake_game import SnakeGame
from scenes.tetris_game import TetrisGame
from scenes.two_guards import TwoGuardsGame

# ── Constants ─────────────────────────────────────────────────────────────────
WIDTH        = 12
HEIGHT       = 8
WINDOW_TITLE = "Adventures"

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── Minigame registry ─────────────────────────────────────────────────────────
# To add a new minigame: import it above, then add one line here.
MINIGAME_REGISTRY: dict = {
    "flappy_bird":     FlappyBirdGame,
    "minesweeper":     MinesweeperGame,
    "nine_puzzle":     NinePuzzleGame,
    "password_puzzle": PasswordPuzzleGame,
    "pong_game":       PongGame,
    "snake_game":      SnakeGame,
    "tetris_game":     TetrisGame,
    "two_guards":      TwoGuardsGame,
}


class SceneManager:
    """Owns scene state and dispatch logic, keeping Game focused on lifecycle."""

    def __init__(self, scenes: list, characters: dict, settings: dict):
        self.scenes     = scenes
        self.characters = characters
        self.settings   = settings
        self.index      = 0

    @property
    def has_next(self) -> bool:
        return self.index < len(self.scenes)

    def next(self) -> dict:
        scene = self.scenes[self.index]
        self.index += 1
        return scene

    def render(self, scene: dict, fig, ax) -> bool:
        """Render a scene. Returns False if the game should stop."""
        scene_type = scene.get("type")

        if scene_type == "conversation":
            location  = scene.get("location")
            bg        = self.settings[location].get("background")
            conversation_cutscene(ax, bg, scene["conversation"], self.characters)

        elif scene_type == "text":
            text_scene(ax, scene, self.settings)

        elif scene_type == "minigame":
            self._run_minigame(scene, fig, ax)

        elif scene_type == "exit":
            return False

        else:
            logger.warning("Unknown scene type: %s", scene_type)

        return True

    def _run_minigame(self, scene: dict, fig, ax) -> None:
        minigame_name = scene.get("game")
        minigame_cls  = MINIGAME_REGISTRY.get(minigame_name)

        if minigame_cls is None:
            logger.error("Unknown minigame: %s — skipping", minigame_name)
            return

        logger.info("Starting minigame: %s", minigame_name)

        # Flappy bird and minesweeper have retry loops driven by score/win
        # All other games run once and return
        if minigame_name == "flappy_bird":
            target_score = scene.get("score_to_beat", 10)
            score        = 0
            while score < target_score:
                game  = minigame_cls(
                    fig, ax, target_score,
                    width=WIDTH, height=HEIGHT,
                    victory_message=scene.get("victory_message", "You win!"),
                    defeat_message=scene.get("defeat_message",  "You lose!"),
                )
                score = game.run()

        elif minigame_name == "minesweeper":
            game_won = False
            while not game_won:
                game     = minigame_cls(fig, ax, width=WIDTH, height=HEIGHT,
                                        num_mines=scene.get("num_mines", 10))
                game_won = game.run()

        elif minigame_name == "password_puzzle":
            game = minigame_cls(
                fig, ax,
                scene.get("clues", []),
                scene.get("password"),
                max_attempts=scene.get("max_attempts", 10),
            )
            game.run()

        elif minigame_name in ("nine_puzzle", "two_guards"):
            # These games have fixed dimensions, no width/height args
            game = minigame_cls(fig, ax)
            game.run()

        else:
            game = minigame_cls(fig, ax, width=WIDTH, height=HEIGHT)
            game.run()


class Game:
    def __init__(self):
        self.running      = False
        self.figure_closed = False
        self.space_pressed = False

        self._load_story()
        self._init_renderer()

    # ── Story loading ──────────────────────────────────────────────────────────

    def _load_story(self) -> None:
        # _MEIPASS is set by PyInstaller at runtime; fall back to script dir
        base_path  = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        story_path = os.path.join(base_path, "data", "story.json")

        try:
            with open(story_path, encoding="utf-8") as f:
                story = json.load(f)
        except FileNotFoundError:
            logger.error("story.json not found at %s", story_path)
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error("story.json is malformed: %s", e)
            sys.exit(1)

        characters = story.get("characters", {})
        settings   = story.get("settings",   {})
        scenes     = story.get("scenes",     [])

        # Normalise scenes — accept both list and dict formats
        if isinstance(scenes, dict):
            scenes = list(scenes.values())

        self.scene_manager = SceneManager(scenes, characters, settings)
        logger.info("Loaded %d scenes", len(scenes))

    # ── Renderer ───────────────────────────────────────────────────────────────

    def _init_renderer(self) -> None:
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(WIDTH, HEIGHT))
        self.ax.margins(0)
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.fig.canvas.manager.set_window_title(WINDOW_TITLE)

        self.fig.canvas.mpl_connect("close_event",     self.on_figure_close)
        self.fig.canvas.mpl_connect("key_press_event", self.on_key_press)

    # ── Event handlers ─────────────────────────────────────────────────────────

    def on_figure_close(self, event) -> None:
        self.figure_closed = True
        self.running       = False
        try:
            plt.close("all")
        except Exception:
            pass  # suppress TclError on Python 3.14 when window already destroyed
        sys.exit(0)

    def on_key_press(self, event) -> None:
        if event.key in (" ", "space"):
            self.space_pressed = True

    def is_figure_closed(self) -> bool:
        if self.figure_closed:
            return True
        try:
            _ = self.fig.canvas
            return False
        except AttributeError:
            return True

    # ── Main loop ──────────────────────────────────────────────────────────────

    def run(self) -> None:
        self.running = True

        while self.running and self.scene_manager.has_next:
            if self.is_figure_closed():
                break

            scene         = self.scene_manager.next()
            should_continue = self.scene_manager.render(scene, self.fig, self.ax)

            if not should_continue:
                self.running = False

        self.cleanup()

    def cleanup(self) -> None:
        logger.info("Game exiting cleanly")
        plt.close("all")


def main() -> None:
    game = Game()
    game.run()


if __name__ == "__main__":
    main()