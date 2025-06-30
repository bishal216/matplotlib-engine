import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

class NinePuzzleGame:
    def __init__(self, fig, ax):
        self.fig = fig
        self.ax = ax
        self.tiles = self.generate_solvable_tiles().reshape((3, 3))
        self.empty = tuple(np.argwhere(self.tiles == 0)[0])  # (row, col)
        self.moves = 0
        self.solved = False
        self.setup_plot()
        self.setup_controls()

    def setup_plot(self):
        self.ax.set_xlim(0, 3)
        self.ax.set_ylim(0, 3)
        self.ax.set_aspect('equal')
        self.ax.set_facecolor('#232946')
        self.ax.grid(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

    def is_solvable(self, tiles):
        arr = [t for t in tiles if t != 0]
        inversions = 0
        for i in range(len(arr)):
            for j in range(i + 1, len(arr)):
                if arr[i] > arr[j]:
                    inversions += 1
        return inversions % 2 == 0

    def generate_solvable_tiles(self):
        tiles = np.arange(0, 9)
        while True:
            np.random.shuffle(tiles)
            if self.is_solvable(tiles):
                return tiles

    def setup_controls(self):
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)

    def on_key(self, event):
        if event.key == 'r':
            self.restart()
        elif event.key == 'q':
            self.quit_game()
            plt.close()

    def on_click(self, event):
        if event.inaxes != self.ax:
            return

        if self.solved:
            self.restart()
            return

        # Convert click to grid coordinates
        col = int(event.xdata)
        row = 2 - int(event.ydata)  # Convert to array row index

        if 0 <= row < 3 and 0 <= col < 3:
            if self.is_adjacent_to_empty(row, col):
                self.move_tile(row, col)

    def is_adjacent_to_empty(self, row, col):
        er, ec = self.empty  # Empty position (row, col)
        return (abs(ec - col) == 1 and er == row) or (abs(er - row) == 1 and ec == col)

    def move_tile(self, row, col):
        er, ec = self.empty  # Empty position (row, col)

        # Swap tile with empty position
        self.tiles[er, ec], self.tiles[row, col] = self.tiles[row, col], self.tiles[er, ec]
        self.empty = (row, col)
        self.moves += 1
        self.check_solved()
        self.draw()

    def restart(self):
        self.tiles = self.generate_solvable_tiles().reshape((3, 3))
        self.empty = tuple(np.argwhere(self.tiles == 0)[0])
        self.moves = 0
        self.solved = False
        self.draw()

    def quit_game(self):
        self.ax.clear()
        self.ax.set_facecolor('#1a1a2e')
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 8)
        self.ax.text(5, 4, "Game Closed", fontsize=30, color='white',
                    ha='center', va='center')
        self.ax.text(5, 3, "Press 'r' to restart or close window", fontsize=15,
                    color='white', ha='center', va='center')

    def check_solved(self):
        if np.array_equal(self.tiles.flatten(), np.append(np.arange(1, 9), 0)):
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

        for row in range(3):
            for col in range(3):
                val = self.tiles[row, col]
                y = 2 - row  # Convert to plot y-coordinate

                if val == 0:
                    # Draw empty tile (invisible)
                    rect = patches.Rectangle(
                        (col, y), 1, 1,
                        facecolor='#232946',
                        edgecolor='white',
                        linewidth=2
                    )
                else:
                    # Draw numbered tile
                    rect = patches.Rectangle(
                        (col, y), 1, 1,
                        facecolor='#eebbc3',
                        edgecolor='black',
                        linewidth=2
                    )
                    self.ax.text(
                        col + 0.5, y + 0.5, str(val),
                        fontsize=24, ha='center', va='center',
                        color='#232946'
                    )
                self.ax.add_patch(rect)

        if self.solved:
            title = f'PUZZLE SOLVED! Moves: {self.moves}\nClick to restart'
            self.ax.set_title(title, fontsize=16, fontweight='bold', color='green')
        else:
            self.ax.set_title(f'Nine Puzzle - Moves: {self.moves}\nPress "r"=Restart, "q"=Quit',
                             fontsize=14, fontweight='bold')
        plt.draw()

    def run(self):
        self.draw()
        while not self.solved:
            plt.pause(0.1)


# # Initialize and run the game
# fig, ax = plt.subplots(figsize=(6, 6))
# fig.canvas.manager.set_window_title('Nine Puzzle Game')
# game = NinePuzzleGame(fig, ax)
# game.run()