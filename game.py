import matplotlib.pyplot as plt
import sys
import os
import json

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


# Constants
WIDTH = 12
HEIGHT = 8
class Game:
    def __init__(self):
        # load story
        self.story = json.load(open('data/story.json'))
        self.characters = self.story.get('characters', {})
        self.settings = self.story.get('settings', {})
        self.scenes = self.story.get('scenes', [])

        # Ensure scenes is a list
        if isinstance(self.scenes, dict):
            self.scenes = list(self.scenes.values())

        self.current_index = 0
        self.running = True
        self.figure_closed = False

        # Create renderer
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(WIDTH, HEIGHT))
        self.ax.margins(0)
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.fig.canvas.manager.set_window_title("Adventures")

        self.fig.canvas.mpl_connect('close_event', self.on_figure_close)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)

    def on_figure_close(self, event):
        self.figure_closed = True
        self.running = False
        plt.close('all')
        sys.exit(0)

    def on_key_press(self, event):
        if event.key == ' ' or event.key == 'space':
            self.space_pressed = True

    def is_figure_closed(self) -> bool:
        if self.figure_closed:
            return True
        try:
            _ = self.fig.canvas
            return False
        except AttributeError:
            return True

    def run(self):
        while self.running and self.current_index < len(self.scenes):
            if self.is_figure_closed():
                break

            scene = self.scenes[self.current_index]
            self.render_scene(scene)
            self.current_index += 1
        self.cleanup()

    def render_scene(self, scene):
        scene_type = scene.get('type')
        if scene_type == 'conversation':
            conversation_cutscene(
                self.ax, self.settings[scene.get('location')].get('background'), scene['conversation'], self.characters)
        elif scene_type == 'text':
            text_scene(self.ax, scene, self.settings)
        elif scene_type == 'minigame':
            minigame_name = scene.get('game')
            if minigame_name == 'flappy_bird':
                target_score = scene.get('score_to_beat', 10)
                score = 0
                while score < target_score:
                    fb = FlappyBirdGame(self.fig, self.ax, target_score, width=WIDTH, height=HEIGHT, victory_message=scene.get("victory_message", "You win!"), defeat_message=scene.get("defeat_message", "You lose!"))
                    score = fb.run()
            elif minigame_name == 'minesweeper':
                game_won = False
                while not game_won:
                    mg = MinesweeperGame(self.fig, self.ax, width=WIDTH, height=HEIGHT, num_mines=scene.get('num_mines', 10))
                    game_won = mg.run()
            elif minigame_name == 'nine_puzzle':
                np_game = NinePuzzleGame(self.fig, self.ax)
                np_game.run()
            elif minigame_name == 'password_puzzle':
                pp_game = PasswordPuzzleGame(self.fig, self.ax, scene.get('clues', []), scene.get('password'))
                pp_game.run()
            elif minigame_name == 'pong_game':
                game = PongGame(self.fig, self.ax)
                game.run()
            elif minigame_name == "snake_game":
                snake_game = SnakeGame(self.fig, self.ax, width=WIDTH, height=HEIGHT)
                snake_game.run()
            elif minigame_name == "tetris_game":
                tetris_game = TetrisGame(self.fig, self.ax, width=WIDTH, height=HEIGHT)
                tetris_game.run()
            elif minigame_name == "two_guards":
                two_guards_game = TwoGuardsGame(self.fig, self.ax)
                two_guards_game.run()


        elif scene_type == 'exit':
            self.running = False

    def cleanup(self):
        plt.close('all')


def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
