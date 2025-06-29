import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import random
import keyboard
import time
from matplotlib.animation import FuncAnimation

class NinePuzzleGame:
    def __init__(self, fig, ax):
        self.fig = fig
        self.ax = ax
        self.tiles = np.arange(1, 10)
        np.random.shuffle(self.tiles)
        self.tiles = self.tiles.reshape((3, 3))
        self.empty = tuple(np.argwhere(self.tiles == 9)[0])
        self.moves = 0
        self.solved = False
        self.setup_plot()
        self.setup_controls()
        
        # Color scheme for tiles
        self.tile_colors = {
            0: '#f0f0f0',  # Empty space
            1: '#ff6b6b',  # Red
            2: '#4ecdc4',  # Teal
            3: '#45b7d1',  # Blue
            4: '#96ceb4',  # Green
            5: '#feca57',  # Yellow
            6: '#ff9ff3',  # Pink
            7: '#54a0ff',  # Light Blue
            8: '#5f27cd'   # Purple
        }
        
    def setup_plot(self):
        self.ax.set_xlim(0, 3)
        self.ax.set_ylim(0, 3)
        self.ax.set_aspect('equal')
        self.ax.set_facecolor('#232946')
        self.ax.grid(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        
    def setup_controls(self):
        """Setup keyboard event handlers"""
        keyboard.on_press_key('up', lambda _: self.move(0, 1))
        keyboard.on_press_key('down', lambda _: self.move(0, -1))
        keyboard.on_press_key('left', lambda _: self.move(1, 0))
        keyboard.on_press_key('right', lambda _: self.move(-1, 0))
        keyboard.on_press_key('r', lambda _: self.restart())
        keyboard.on_press_key('escape', lambda _: self.quit_game())
        
    def move(self, dx, dy):
        if self.solved: return
        ex, ey = self.empty
        nx, ny = ex + dx, ey + dy
        if 0 <= nx < 3 and 0 <= ny < 3:
            self.tiles[ey, ex], self.tiles[ny, nx] = self.tiles[ny, nx], self.tiles[ey, ex]
            self.empty = (nx, ny)
            self.moves += 1
            self.check_solved()
            self.draw()
    
    def restart(self):
        self.tiles = np.arange(1, 10)
        np.random.shuffle(self.tiles)
        self.tiles = self.tiles.reshape((3, 3))
        self.empty = tuple(np.argwhere(self.tiles == 9)[0])
        self.moves = 0
        self.solved = False
        self.ax.set_title('Nine Puzzle', fontsize=16, fontweight='bold')
        plt.draw()
    
    def quit_game(self):
        self.solved = True
        self.ax.clear()
        self.ax.set_facecolor('#1a1a2e')
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 8)
        self.ax.set_aspect('equal')
        self.ax.grid(False)
    
    def check_solved(self):
        if np.array_equal(self.tiles.flatten(), np.arange(1, 10)):
            self.solved = True
    
    def draw(self):
        self.ax.clear()
        self.ax.set_xlim(0, 3)
        self.ax.set_ylim(0, 3)
        self.ax.set_aspect('equal')
        self.ax.set_facecolor('#232946')
        self.ax.grid(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for y in range(3):
            for x in range(3):
                val = self.tiles[y, x]
                if val != 9:
                    self.ax.add_patch(patches.Rectangle((x, 2 - y), 1, 1, facecolor='#eebbc3', edgecolor='black'))
                    self.ax.text(x + 0.5, 2 - y + 0.5, str(val), fontsize=24, ha='center', va='center', color='#232946')
        if self.solved:
            self.ax.set_title(f'YOU WIN! Moves: {self.moves}\nR: Restart, ESC: Quit', fontsize=16, fontweight='bold', color='green')
        else:
            self.ax.set_title(f'Nine Puzzle - Moves: {self.moves}', fontsize=16, fontweight='bold')
        self.ax.text(0.5, 0.1, 'Arrows: Move | R: Restart | ESC: Quit', transform=self.ax.transAxes, fontsize=10, color='#b8c1ec')
    
    def run(self):
        print('Nine Puzzle Game Started!')
        print('Controls: Arrows=Move, R=Restart, ESC=Quit')
        self.draw()
        while not self.solved:
            plt.pause(0.1)

def run_nine_puzzle_game(fig, ax):
    try:
        game = NinePuzzleGame(fig, ax)
        game.run()
    except KeyboardInterrupt:
        print('\nGame stopped by user')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    fig, ax = plt.subplots(figsize=(3, 3))
    run_nine_puzzle_game(fig, ax) 