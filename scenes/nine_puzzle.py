import logging

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────
GRID_SIZE      = 3
PAUSE_INTERVAL = 0.05   # seconds between event polls
SOLVED_ORDER   = np.append(np.arange(1, GRID_SIZE ** 2), 0)

# Colours
BG_COLOR       = "#232946"
TILE_COLOR     = "#eebbc3"
TILE_TEXT      = "#232946"
EMPTY_COLOR    = "#232946"


class NinePuzzleGame:
    def __init__(self, fig, ax):
        self.fig   = fig
        self.ax    = ax
        self.moves = 0
        self.solved = False

        self.tiles = self._generate_solvable_tiles()
        self.empty = tuple(np.argwhere(self.tiles == 0)[0])  # (row, col)

        self._click_cid = self.fig.canvas.mpl_connect("button_press_event", self._on_click)
        self._key_cid   = self.fig.canvas.mpl_connect("key_press_event",   self._on_key)

    # ── Puzzle generation ──────────────────────────────────────────────────────

    def _is_solvable(self, tiles: np.ndarray) -> bool:
        """Count inversions — puzzle is solvable iff inversion count is even."""
        flat       = tiles[tiles != 0]
        inversions = int(np.sum(np.fromiter(
            (np.sum(flat[i] > flat[i + 1:]) for i in range(len(flat))),
            dtype=int,
        )))
        return inversions % 2 == 0

    def _generate_solvable_tiles(self) -> np.ndarray:
        tiles = np.arange(GRID_SIZE ** 2)
        while True:
            np.random.shuffle(tiles)
            if self._is_solvable(tiles):
                return tiles.reshape((GRID_SIZE, GRID_SIZE))

    # ── Input ──────────────────────────────────────────────────────────────────

    def _on_click(self, event) -> None:
        if event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            return

        col = int(event.xdata)
        row = (GRID_SIZE - 1) - int(event.ydata)   # flip y → array row

        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            if not self.solved and self._is_adjacent_to_empty(row, col):
                self._move_tile(row, col)

    def _on_key(self, event) -> None:
        # Arrow key support — move the tile adjacent to the empty space
        key_to_delta = {
            "up":    ( 1,  0),
            "down":  (-1,  0),
            "left":  ( 0,  1),
            "right": ( 0, -1),
        }
        if event.key not in key_to_delta or self.solved:
            return

        er, ec    = self.empty
        dr, dc    = key_to_delta[event.key]
        row, col  = er + dr, ec + dc

        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            self._move_tile(row, col)

    # ── Game logic ─────────────────────────────────────────────────────────────

    def _is_adjacent_to_empty(self, row: int, col: int) -> bool:
        er, ec = self.empty
        return (abs(ec - col) == 1 and er == row) or \
               (abs(er - row) == 1 and ec == col)

    def _move_tile(self, row: int, col: int) -> None:
        er, ec = self.empty
        self.tiles[er, ec], self.tiles[row, col] = \
            self.tiles[row, col], self.tiles[er, ec]
        self.empty = (row, col)
        self.moves += 1
        self._check_solved()
        self._draw()

    def _check_solved(self) -> None:
        if np.array_equal(self.tiles.flatten(), SOLVED_ORDER):
            self.solved = True
            logger.debug("Nine puzzle solved in %d moves", self.moves)

    # ── Drawing ────────────────────────────────────────────────────────────────

    def _setup_axes(self) -> None:
        self.ax.clear()
        self.ax.set_xlim(0, GRID_SIZE)
        self.ax.set_ylim(0, GRID_SIZE)
        self.ax.set_aspect("equal")
        self.ax.set_facecolor(BG_COLOR)
        self.ax.grid(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

    def _draw(self) -> None:
        self._setup_axes()

        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                val = self.tiles[row, col]
                y   = (GRID_SIZE - 1) - row   # flip row → plot y

                if val == 0:
                    self.ax.add_patch(patches.Rectangle(
                        (col, y), 1, 1,
                        facecolor=EMPTY_COLOR, edgecolor="white", linewidth=2,
                    ))
                else:
                    self.ax.add_patch(patches.Rectangle(
                        (col, y), 1, 1,
                        facecolor=TILE_COLOR, edgecolor="black", linewidth=2,
                    ))
                    self.ax.text(
                        col + 0.5, y + 0.5, str(val),
                        fontsize=24, ha="center", va="center", color=TILE_TEXT,
                    )

        if self.solved:
            self.ax.set_title(
                f"PUZZLE SOLVED in {self.moves} moves!\nPress space to continue",
                fontsize=16, fontweight="bold", color="green",
            )
        else:
            self.ax.set_title(
                f"Nine Puzzle — Moves: {self.moves}\nClick or use arrow keys to move tiles",
                fontsize=14, fontweight="bold", color="white",
            )

        self.fig.canvas.draw_idle()

    # ── Cleanup ────────────────────────────────────────────────────────────────

    def _disconnect(self) -> None:
        self.fig.canvas.mpl_disconnect(self._click_cid)
        self.fig.canvas.mpl_disconnect(self._key_cid)

    # ── Public API ─────────────────────────────────────────────────────────────

    def run(self) -> None:
        self._draw()

        while not self.solved:
            plt.pause(PAUSE_INTERVAL)

        # Wait for space/click to dismiss
        continue_flag = {"clicked": False}

        def on_click(event):
            continue_flag["clicked"] = True

        def on_key(event):
            if event.key in (" ", "space"):
                continue_flag["clicked"] = True

        cid_click = self.fig.canvas.mpl_connect("button_press_event", on_click)
        cid_key   = self.fig.canvas.mpl_connect("key_press_event",   on_key)

        try:
            while not continue_flag["clicked"]:
                plt.pause(PAUSE_INTERVAL)
        finally:
            self.fig.canvas.mpl_disconnect(cid_click)
            self.fig.canvas.mpl_disconnect(cid_key)
            self._disconnect()