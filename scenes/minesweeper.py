import random
import logging
from collections import deque

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────
ANIM_INTERVAL = 100  # ms between frames
PAUSE_INTERVAL = 0.05  # seconds between event polls

# Cell colours
COLOR_HIDDEN = "gray"
COLOR_REVEALED = "lightgray"
COLOR_MINE = "red"
COLOR_FLAG = "yellow"

# Number colours (standard Minesweeper palette)
NUMBER_COLORS = {
    1: "#0000ff",
    2: "#008200",
    3: "#ff0000",
    4: "#000084",
    5: "#840000",
    6: "#008284",
    7: "#840084",
    8: "#757575",
}

NEIGHBORS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


class MinesweeperGame:
    def __init__(self, fig, ax, width: int = 10, height: int = 10, num_mines: int = 15):
        self.fig = fig
        self.ax = ax
        self.width = width
        self.height = height
        self.num_mines = num_mines

        self._reset_state()
        self._click_cid = self.fig.canvas.mpl_connect(
            "button_press_event", self._on_click
        )

    # ── State ──────────────────────────────────────────────────────────────────

    def _reset_state(self) -> None:
        self.board = np.zeros((self.height, self.width), dtype=int)
        self.revealed = np.zeros((self.height, self.width), dtype=bool)
        self.flagged = np.zeros((self.height, self.width), dtype=bool)
        self.game_over = False
        self.game_won = False
        self.first_click = True

    # ── Mine placement ─────────────────────────────────────────────────────────

    def _place_mines(self, safe_x: int, safe_y: int) -> None:
        """Place mines after first click, guaranteeing the first cell is safe."""
        all_cells = [(x, y) for x in range(self.width) for y in range(self.height)]
        all_cells.remove((safe_x, safe_y))
        mine_cells = random.sample(all_cells, self.num_mines)

        for x, y in mine_cells:
            self.board[y, x] = -1

        # Calculate neighbor counts
        for x, y in mine_cells:
            for dy, dx in NEIGHBORS:
                ny, nx = y + dy, x + dx
                if (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                    and self.board[ny, nx] != -1
                ):
                    self.board[ny, nx] += 1

        logger.debug("Mines placed — safe start: (%d, %d)", safe_x, safe_y)

    # ── Input ──────────────────────────────────────────────────────────────────

    def _on_click(self, event) -> None:
        if self.game_over or self.game_won:
            return
        if event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            return

        x, y = int(event.xdata), int(event.ydata)
        if not (0 <= x < self.width and 0 <= y < self.height):
            return

        if event.button == 1:
            self._reveal_cell(x, y)
        elif event.button == 3:
            self._toggle_flag(x, y)

    # ── Game logic ─────────────────────────────────────────────────────────────

    def _reveal_cell(self, x: int, y: int) -> None:
        if self.revealed[y, x] or self.flagged[y, x]:
            return

        if self.first_click:
            self._place_mines(x, y)
            self.first_click = False

        if self.board[y, x] == -1:
            self.revealed[y, x] = True
            self.game_over = True
            self._reveal_all_mines()
            logger.debug("Mine hit at (%d, %d)", x, y)
            return

        # Iterative flood-fill — avoids recursion limit on large empty areas
        queue = deque([(x, y)])
        while queue:
            cx, cy = queue.popleft()
            if self.revealed[cy, cx] or self.flagged[cy, cx]:
                continue
            self.revealed[cy, cx] = True
            if self.board[cy, cx] == 0:
                for dy, dx in NEIGHBORS:
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        queue.append((nx, ny))

        self._check_win()

    def _toggle_flag(self, x: int, y: int) -> None:
        if not self.revealed[y, x]:
            self.flagged[y, x] = not self.flagged[y, x]

    def _reveal_all_mines(self) -> None:
        self.revealed[self.board == -1] = True

    def _check_win(self) -> None:
        # Win when every non-mine cell is revealed
        unrevealed_safe = (~self.revealed) & (self.board != -1)
        if not unrevealed_safe.any():
            self.game_won = True
            logger.debug("Game won")

    # ── Drawing ────────────────────────────────────────────────────────────────

    def _draw(self) -> None:
        self.ax.clear()
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.set_aspect("equal")
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        # Title / status
        if self.game_over:
            self.ax.set_title(
                "GAME OVER! You hit a mine!",
                fontsize=16,
                fontweight="bold",
                color="red",
            )
        elif self.game_won:
            self.ax.set_title(
                "YOU WIN! All mines found!",
                fontsize=16,
                fontweight="bold",
                color="green",
            )
        else:
            flags_remaining = self.num_mines - int(self.flagged.sum())
            self.ax.set_title(
                f"Minesweeper — Mines remaining: {flags_remaining}",
                fontsize=16,
                fontweight="bold",
            )

        # Cells
        for y in range(self.height):
            for x in range(self.width):
                self._draw_cell(x, y)

        # Instructions overlay
        self.ax.text(
            0.02,
            0.98,
            "Left click: Reveal   Right click: Flag",
            transform=self.ax.transAxes,
            fontsize=9,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
        )

    def _draw_cell(self, x: int, y: int) -> None:
        if self.revealed[y, x]:
            value = self.board[y, x]
            color = COLOR_MINE if value == -1 else COLOR_REVEALED
            self.ax.add_patch(
                patches.Rectangle(
                    (x, y),
                    1,
                    1,
                    facecolor=color,
                    edgecolor="black",
                    linewidth=1,
                )
            )
            if value == -1:
                self.ax.text(
                    x + 0.5,
                    y + 0.5,
                    "*",
                    fontsize=14,
                    ha="center",
                    va="center",
                    color="white",
                    fontweight="bold",
                )
            elif value > 0:
                self.ax.text(
                    x + 0.5,
                    y + 0.5,
                    str(value),
                    fontsize=14,
                    ha="center",
                    va="center",
                    color=NUMBER_COLORS.get(value, "black"),
                    fontweight="bold",
                )

        elif self.flagged[y, x]:
            self.ax.add_patch(
                patches.Rectangle(
                    (x, y),
                    1,
                    1,
                    facecolor=COLOR_FLAG,
                    edgecolor="black",
                    linewidth=1,
                )
            )
            self.ax.text(
                x + 0.5,
                y + 0.5,
                "F",
                fontsize=14,
                ha="center",
                va="center",
                color="red",
                fontweight="bold",
            )

        else:
            self.ax.add_patch(
                patches.Rectangle(
                    (x, y),
                    1,
                    1,
                    facecolor=COLOR_HIDDEN,
                    edgecolor="black",
                    linewidth=1,
                )
            )

    # ── Animation ──────────────────────────────────────────────────────────────

    def _update(self, frame) -> list:
        self._draw()
        return []

    # ── Cleanup ────────────────────────────────────────────────────────────────

    def _disconnect(self) -> None:
        self.fig.canvas.mpl_disconnect(self._click_cid)

    # ── Public API ─────────────────────────────────────────────────────────────

    def run(self) -> bool:
        self.anim = FuncAnimation(
            self.fig,
            self._update,
            interval=ANIM_INTERVAL,
            blit=False,
            repeat=True,
            cache_frame_data=False,
        )

        try:
            while not self.game_over and not self.game_won:
                plt.pause(PAUSE_INTERVAL)
        finally:
            self.anim.event_source.stop()
            self._disconnect()

        # Brief pause so player can see the final board state
        end_flag = {"clicked": False}

        def on_click(event):
            end_flag["clicked"] = True

        def on_key(event):
            if event.key in (" ", "space"):
                end_flag["clicked"] = True

        cid_click = self.fig.canvas.mpl_connect("button_press_event", on_click)
        cid_key = self.fig.canvas.mpl_connect("key_press_event", on_key)

        try:
            while not end_flag["clicked"]:
                plt.pause(PAUSE_INTERVAL)
        finally:
            self.fig.canvas.mpl_disconnect(cid_click)
            self.fig.canvas.mpl_disconnect(cid_key)

        return self.game_won
