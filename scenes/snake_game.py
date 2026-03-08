import random
import logging
from collections import deque

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────
ANIM_INTERVAL = 200  # ms between frames (controls snake speed)
PAUSE_INTERVAL = 0.05  # seconds between event polls

FOOD_SCORE = 10

# Colours
BG_COLOR = "black"
HEAD_COLOR = "darkgreen"
BODY_COLOR = "green"
FOOD_COLOR = "red"

# Direction vectors
DIR_UP = (0, 1)
DIR_DOWN = (0, -1)
DIR_LEFT = (-1, 0)
DIR_RIGHT = (1, 0)

KEY_TO_DIR = {
    "up": DIR_UP,
    "down": DIR_DOWN,
    "left": DIR_LEFT,
    "right": DIR_RIGHT,
}


class SnakeGame:
    def __init__(self, fig, ax, width: int = 20, height: int = 20):
        self.fig = fig
        self.ax = ax
        self.width = width
        self.height = height

        self._reset_state()

        self._key_cid = self.fig.canvas.mpl_connect("key_press_event", self._on_key)

    # ── State ──────────────────────────────────────────────────────────────────

    def _reset_state(self) -> None:
        start = (self.width // 2, self.height // 2)
        self.snake = deque([start])  # deque for O(1) head insert / tail pop
        self.snake_set = {start}  # set for O(1) collision lookup
        self.direction = DIR_RIGHT
        self._queued_dir = DIR_RIGHT  # buffered input applied once per frame
        self.food = self._generate_food()
        self.score = 0
        self.game_over = False

    # ── Food ───────────────────────────────────────────────────────────────────

    def _generate_food(self) -> tuple:
        all_cells = {(x, y) for x in range(self.width) for y in range(self.height)}
        free = list(all_cells - self.snake_set)
        if not free:
            logger.warning("No free cells for food — board is full!")
            return self.snake[-1]  # fallback: place on tail (about to vacate)
        return random.choice(free)

    # ── Input ──────────────────────────────────────────────────────────────────

    def _on_key(self, event) -> None:
        new_dir = KEY_TO_DIR.get(event.key)
        if new_dir is None or self.game_over:
            return
        # Prevent 180-degree reversal
        if new_dir[0] != -self.direction[0] or new_dir[1] != -self.direction[1]:
            self._queued_dir = new_dir

    # ── Game logic ─────────────────────────────────────────────────────────────

    def _move_snake(self) -> None:
        if self.game_over:
            return

        # Apply buffered direction once per frame
        self.direction = self._queued_dir

        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])

        # Wall collision
        if not (0 <= new_head[0] < self.width and 0 <= new_head[1] < self.height):
            self.game_over = True
            logger.debug("Wall collision at %s — score: %d", new_head, self.score)
            return

        # Self collision — O(1) via set
        if new_head in self.snake_set:
            self.game_over = True
            logger.debug("Self collision at %s — score: %d", new_head, self.score)
            return

        # Move head
        self.snake.appendleft(new_head)
        self.snake_set.add(new_head)

        # Food eaten
        if new_head == self.food:
            self.score += FOOD_SCORE
            self.food = self._generate_food()
            logger.debug("Food eaten — score: %d", self.score)
            # Don't pop tail — snake grows
        else:
            tail = self.snake.pop()
            self.snake_set.discard(tail)

    # ── Drawing ────────────────────────────────────────────────────────────────

    def _setup_axes(self) -> None:
        self.ax.clear()
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.set_aspect("equal")
        self.ax.set_facecolor(BG_COLOR)
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

    def _draw(self) -> None:
        self._setup_axes()

        # Snake
        for i, segment in enumerate(self.snake):
            self.ax.add_patch(
                patches.Rectangle(
                    segment,
                    1,
                    1,
                    facecolor=HEAD_COLOR if i == 0 else BODY_COLOR,
                    edgecolor="black",
                    linewidth=1,
                )
            )

        # Food
        self.ax.add_patch(
            patches.Rectangle(
                self.food,
                1,
                1,
                facecolor=FOOD_COLOR,
                edgecolor="black",
                linewidth=1,
            )
        )

        # HUD
        if self.game_over:
            self.ax.set_title(
                f"GAME OVER!  Score: {self.score}\nPress space or click to continue",
                fontsize=16,
                fontweight="bold",
                color="red",
            )
        else:
            self.ax.set_title(
                f"Snake — Score: {self.score}   Arrow keys to move",
                fontsize=14,
                fontweight="bold",
                color="white",
            )

    # ── Animation ──────────────────────────────────────────────────────────────

    def _update(self, frame) -> list:
        self._move_snake()
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
