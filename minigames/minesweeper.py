import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import random
import keyboard
import time
from matplotlib.animation import FuncAnimation

class MinesweeperGame:
    def __init__(self, fig, ax, width=10, height=10, num_mines=15):
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.board = np.zeros((height, width), dtype=int)
        self.revealed = np.zeros((height, width), dtype=bool)
        self.flagged = np.zeros((height, width), dtype=bool)
        self.game_over = False
        self.game_won = False
        self.first_click = True
        self.mines_placed = False
        self.fig = fig
        self.ax = ax
        self.setup_plot()
        self.setup_controls()
        self.number_colors = {
            1: '#0000ff', 2: '#008200', 3: '#ff0000', 4: '#000084',
            5: '#840000', 6: '#008284', 7: '#840084', 8: '#757575'
        }
    def setup_plot(self):
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.set_aspect('equal')
        self.ax.set_title(f'Minesweeper - Mines: {self.num_mines}', fontsize=16, fontweight='bold')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
    def setup_controls(self):
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        keyboard.on_press_key('r', lambda _: self.restart())
        keyboard.on_press_key('escape', lambda _: self.quit_game())
    def on_click(self, event):
        if self.game_over or self.game_won: return
        if event.inaxes != self.ax: return
        x, y = int(event.xdata), int(event.ydata)
        if 0 <= x < self.width and 0 <= y < self.height:
            if event.button == 1: self.reveal_cell(x, y)
            elif event.button == 3: self.toggle_flag(x, y)
    def place_mines(self, first_x, first_y):
        positions = [(x, y) for x in range(self.width) for y in range(self.height)]
        positions.remove((first_x, first_y))
        mine_positions = random.sample(positions, self.num_mines)
        for x, y in mine_positions: self.board[y, x] = -1
        for x, y in mine_positions:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < self.width and 0 <= ny < self.height and self.board[ny, nx] != -1):
                        self.board[ny, nx] += 1
        self.mines_placed = True
    def reveal_cell(self, x, y):
        if self.revealed[y, x] or self.flagged[y, x]: return
        if self.first_click:
            self.place_mines(x, y)
            self.first_click = False
        self.revealed[y, x] = True
        if self.board[y, x] == -1:
            self.game_over = True
            self.reveal_all_mines()
            return
        if self.board[y, x] == 0:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < self.width and 0 <= ny < self.height and not self.revealed[ny, nx] and not self.flagged[ny, nx]):
                        self.reveal_cell(nx, ny)
        self.check_win()
    def toggle_flag(self, x, y):
        if not self.revealed[y, x]: self.flagged[y, x] = not self.flagged[y, x]
    def reveal_all_mines(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y, x] == -1: self.revealed[y, x] = True
    def check_win(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y, x] != -1 and not self.revealed[y, x]: return
        self.game_won = True
    def restart(self):
        self.board = np.zeros((self.height, self.width), dtype=int)
        self.revealed = np.zeros((self.height, self.width), dtype=bool)
        self.flagged = np.zeros((self.height, self.width), dtype=bool)
        self.game_over = False
        self.game_won = False
        self.first_click = True
        self.mines_placed = False
        self.ax.set_title(f'Minesweeper - Mines: {self.num_mines}', fontsize=16, fontweight='bold')
        plt.draw()
    def quit_game(self):
        self.game_over = True
        self.ax.clear()
        self.ax.set_facecolor('#1a1a2e')
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 8)
        self.ax.set_aspect('equal')
        self.ax.grid(False)
    def draw(self):
        self.ax.clear()
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        if self.game_over:
            self.ax.set_title(f'GAME OVER! You hit a mine!\nPress R to restart or ESC to quit', fontsize=16, fontweight='bold', color='red')
        elif self.game_won:
            self.ax.set_title(f'YOU WIN! All mines found!\nPress R to restart or ESC to quit', fontsize=16, fontweight='bold', color='green')
        else:
            self.ax.set_title(f'Minesweeper - Mines: {self.num_mines}', fontsize=16, fontweight='bold')
        for y in range(self.height):
            for x in range(self.width):
                if self.revealed[y, x]:
                    if self.board[y, x] == -1:
                        cell = patches.Rectangle((x, y), 1, 1, facecolor='red', edgecolor='black', linewidth=1)
                        self.ax.add_patch(cell)
                        self.ax.text(x + 0.5, y + 0.5, 'X', fontsize=16, ha='center', va='center', color='red', fontweight='bold')
                    elif self.board[y, x] > 0:
                        cell = patches.Rectangle((x, y), 1, 1, facecolor='lightgray', edgecolor='black', linewidth=1)
                        self.ax.add_patch(cell)
                        color = self.number_colors.get(self.board[y, x], 'black')
                        self.ax.text(x + 0.5, y + 0.5, str(self.board[y, x]), fontsize=14, ha='center', va='center', color=color, fontweight='bold')
                    else:
                        cell = patches.Rectangle((x, y), 1, 1, facecolor='lightgray', edgecolor='black', linewidth=1)
                        self.ax.add_patch(cell)
                elif self.flagged[y, x]:
                    cell = patches.Rectangle((x, y), 1, 1, facecolor='yellow', edgecolor='black', linewidth=1)
                    self.ax.add_patch(cell)
                    self.ax.text(x + 0.5, y + 0.5, 'F', fontsize=14, ha='center', va='center', color='red', fontweight='bold')
                else:
                    cell = patches.Rectangle((x, y), 1, 1, facecolor='gray', edgecolor='black', linewidth=1)
                    self.ax.add_patch(cell)
        instructions = ("Left click: Reveal\nRight click: Flag\nR: Restart, ESC: Quit")
        self.ax.text(0.02, 0.98, instructions, transform=self.ax.transAxes, fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    def update(self, frame):
        self.draw()
        return []
    def run(self):
        print("Minesweeper Game Started!")
        print("Controls:")
        print("- Left click: Reveal cell")
        print("- Right click: Flag/unflag cell")
        print("- R: Restart game")
        print("- ESC: Return to main menu")
        self.anim = FuncAnimation(self.fig, self.update, interval=100, blit=False, repeat=True, cache_frame_data=False)
        self.anim.event_source.start()
        while not self.game_over and not self.game_won:
            plt.pause(0.1)
        self.anim.event_source.stop()

def run_minesweeper_game(fig, ax):
    try:
        game = MinesweeperGame(fig, ax)
        game.run()
    except KeyboardInterrupt:
        print("\nGame stopped by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 10))
    run_minesweeper_game(fig, ax) 