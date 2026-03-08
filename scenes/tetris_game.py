import random
import logging

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────
ANIM_INTERVAL = 50  # ms between frames
PAUSE_INTERVAL = 0.05  # seconds between event polls

DROP_FRAMES_INIT = 20  # frames between auto-drops at start
DROP_FRAMES_MIN = 5  # fastest auto-drop speed
DROP_SPEED_EVERY = 10  # lines cleared before speeding up

HARD_DROP_BONUS = 2  # points per cell for hard drop
LINE_SCORE_BASE = 100  # multiplied by lines^2

# Colours
BG_COLOR = "black"
GHOST_ALPHA = 0.25  # ghost piece opacity

# Piece definitions — shape + colour stored together
PIECES = {
    "I": {"shape": np.array([[1, 1, 1, 1]]), "color": "cyan"},
    "O": {"shape": np.array([[1, 1], [1, 1]]), "color": "yellow"},
    "T": {"shape": np.array([[0, 1, 0], [1, 1, 1]]), "color": "purple"},
    "S": {"shape": np.array([[0, 1, 1], [1, 1, 0]]), "color": "green"},
    "Z": {"shape": np.array([[1, 1, 0], [0, 1, 1]]), "color": "red"},
    "J": {"shape": np.array([[1, 0, 0], [1, 1, 1]]), "color": "blue"},
    "L": {"shape": np.array([[0, 0, 1], [1, 1, 1]]), "color": "orange"},
}

# Map colour name → index stored in board (0 = empty)
COLOR_INDEX = {name: i + 1 for i, name in enumerate(PIECES)}
INDEX_COLOR = {v: PIECES[k]["color"] for k, v in COLOR_INDEX.items()}


class TetrisGame:
    def __init__(self, fig, ax, width: int = 10, height: int = 20):
        self.fig = fig
        self.ax = ax
        self.width = width
        self.height = height

        self._reset_state()

        self._key_cid = self.fig.canvas.mpl_connect("key_press_event", self._on_key)

    # ── State ──────────────────────────────────────────────────────────────────

    def _reset_state(self) -> None:
        # Board stores colour index (0 = empty, 1-7 = piece colour)
        self.board = np.zeros((self.height, self.width), dtype=int)
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False
        self._frame_counter = 0
        self._drop_frames = DROP_FRAMES_INIT

        self.current_piece = None
        self.current_color = None
        self.current_x = 0
        self.current_y = 0

        self._new_piece()

    # ── Piece management ───────────────────────────────────────────────────────

    def _new_piece(self) -> None:
        name = random.choice(list(PIECES.keys()))
        self.current_piece = PIECES[name]["shape"].copy()
        self.current_color = name
        self.current_x = self.width // 2 - self.current_piece.shape[1] // 2
        self.current_y = self.height - 1

        if not self._is_valid(self.current_piece, self.current_x, self.current_y):
            self.game_over = True
            logger.debug("Game over — no room for new piece")

    def _is_valid(self, piece: np.ndarray, x: int, y: int) -> bool:
        for i in range(piece.shape[0]):
            for j in range(piece.shape[1]):
                if piece[i, j]:
                    nx, ny = x + j, y - i
                    if nx < 0 or nx >= self.width or ny < 0 or ny >= self.height:
                        return False
                    if self.board[ny, nx]:
                        return False
        return True

    def _place_piece(self) -> None:
        color_idx = COLOR_INDEX[self.current_color]
        for i in range(self.current_piece.shape[0]):
            for j in range(self.current_piece.shape[1]):
                if self.current_piece[i, j]:
                    self.board[self.current_y - i, self.current_x + j] = color_idx

    def _clear_lines(self) -> None:
        full_rows = [i for i in range(self.height) if np.all(self.board[i])]
        if not full_rows:
            return

        self.board = np.delete(self.board, full_rows, axis=0)
        self.board = np.vstack(
            [
                self.board,
                np.zeros((len(full_rows), self.width), dtype=int),
            ]
        )

        n = len(full_rows)
        self.lines_cleared += n
        self.score += n * n * LINE_SCORE_BASE
        logger.debug("Cleared %d lines — score: %d", n, self.score)

        # Speed up every DROP_SPEED_EVERY lines
        level = self.lines_cleared // DROP_SPEED_EVERY
        self._drop_frames = max(DROP_FRAMES_MIN, DROP_FRAMES_INIT - level * 2)

    # ── Ghost piece ────────────────────────────────────────────────────────────

    def _ghost_y(self) -> int:
        """Find the lowest valid Y position for the current piece."""
        ghost_y = self.current_y
        while self._is_valid(self.current_piece, self.current_x, ghost_y - 1):
            ghost_y -= 1
        return ghost_y

    # ── Input ──────────────────────────────────────────────────────────────────

    def _on_key(self, event) -> None:
        if self.game_over:
            return

        key = event.key

        if key == "left":
            self._move(dx=-1, dy=0)
        elif key == "right":
            self._move(dx=1, dy=0)
        elif key == "down":
            self._move(dx=0, dy=-1)
        elif key == "up":
            self._rotate()
        elif key == " ":
            self._hard_drop()

    # ── Movement ───────────────────────────────────────────────────────────────

    def _move(self, dx: int, dy: int) -> None:
        nx, ny = self.current_x + dx, self.current_y + dy
        if self._is_valid(self.current_piece, nx, ny):
            self.current_x, self.current_y = nx, ny
        elif dy < 0:
            self._land_piece()

    def _rotate(self) -> None:
        rotated = np.rot90(self.current_piece)
        if self._is_valid(rotated, self.current_x, self.current_y):
            self.current_piece = rotated

    def _hard_drop(self) -> None:
        while self._is_valid(self.current_piece, self.current_x, self.current_y - 1):
            self.current_y -= 1
            self.score += HARD_DROP_BONUS
        self._land_piece()

    def _land_piece(self) -> None:
        self._place_piece()
        self._clear_lines()
        self._new_piece()

    # ── Drawing ────────────────────────────────────────────────────────────────

    def _setup_axes(self) -> None:
        self.ax.clear()
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.set_aspect("equal")
        self.ax.set_facecolor(BG_COLOR)
        self.ax.grid(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

    def _draw_cell(self, x: int, y: int, color: str, alpha: float = 1.0) -> None:
        self.ax.add_patch(
            patches.Rectangle(
                (x, y),
                1,
                1,
                facecolor=color,
                edgecolor="black",
                linewidth=1,
                alpha=alpha,
            )
        )

    def _draw(self) -> None:
        self._setup_axes()

        # Placed board cells — coloured by piece type
        for y in range(self.height):
            for x in range(self.width):
                idx = self.board[y, x]
                if idx:
                    self._draw_cell(x, y, INDEX_COLOR[idx])

        # Ghost piece
        ghost_y = self._ghost_y()
        if ghost_y != self.current_y:
            for i in range(self.current_piece.shape[0]):
                for j in range(self.current_piece.shape[1]):
                    if self.current_piece[i, j]:
                        self._draw_cell(
                            self.current_x + j,
                            ghost_y - i,
                            PIECES[self.current_color]["color"],
                            alpha=GHOST_ALPHA,
                        )

        # Current piece
        color = PIECES[self.current_color]["color"]
        for i in range(self.current_piece.shape[0]):
            for j in range(self.current_piece.shape[1]):
                if self.current_piece[i, j]:
                    self._draw_cell(self.current_x + j, self.current_y - i, color)

        # HUD
        level = self.lines_cleared // DROP_SPEED_EVERY + 1
        if self.game_over:
            self.ax.set_title(
                f"GAME OVER!  Score: {self.score}\nPress space or click to continue",
                fontsize=16,
                fontweight="bold",
                color="red",
            )
        else:
            self.ax.set_title(
                f"Tetris — Score: {self.score}  Lines: {self.lines_cleared}  Level: {level}",
                fontsize=14,
                fontweight="bold",
                color="white",
            )

        # Instructions
        self.ax.text(
            0.02,
            0.98,
            "← → move   ↑ rotate   ↓ soft drop   space hard drop",
            transform=self.ax.transAxes,
            fontsize=8,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.15),
            color="white",
        )

    # ── Animation ──────────────────────────────────────────────────────────────

    def _update(self, frame) -> list:
        if not self.game_over:
            self._frame_counter += 1
            if self._frame_counter >= self._drop_frames:
                self._frame_counter = 0
                self._move(dx=0, dy=-1)

        self._draw()
        return []

    # ── Cleanup ────────────────────────────────────────────────────────────────

    def _disconnect(self) -> None:
        self.fig.canvas.mpl_disconnect(self._key_cid)

    # ── Public API ─────────────────────────────────────────────────────────────

    def run(self) -> int:
        self.anim = FuncAnimation(
            self.fig,
            self._update,
            interval=ANIM_INTERVAL,
            blit=False,
            repeat=True,
            cache_frame_data=False,
        )

        try:
            while not self.game_over:
                plt.pause(PAUSE_INTERVAL)
        finally:
            self.anim.event_source.stop()

        self._draw()

        # Wait for space or click to dismiss
        continue_flag = {"clicked": False}

        def on_click(event):
            continue_flag["clicked"] = True

        def on_key(event):
            if event.key in (" ", "space"):
                continue_flag["clicked"] = True

        cid_click = self.fig.canvas.mpl_connect("button_press_event", on_click)
        cid_key = self.fig.canvas.mpl_connect("key_press_event", on_key)

        try:
            while not continue_flag["clicked"]:
                plt.pause(PAUSE_INTERVAL)
        finally:
            self.fig.canvas.mpl_disconnect(cid_click)
            self.fig.canvas.mpl_disconnect(cid_key)
            self._disconnect()

        return self.score
