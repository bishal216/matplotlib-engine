import logging

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────
ANIM_INTERVAL = 30  # ms between frames
PAUSE_INTERVAL = 0.01  # seconds between event polls

PADDLE_WIDTH = 0.3
PADDLE_HEIGHT = 2.0
PADDLE_X = 1.0
PADDLE_SPEED = 0.3

BALL_RADIUS = 0.3
BALL_INIT_VEL = [0.15, 0.12]
SPEED_INCREMENT = 0.01  # added to ball speed on each paddle hit
MAX_SPEED = 0.5  # cap so it never becomes unplayable

# Colours
BG_COLOR = "black"
PADDLE_COLOR = "white"
BALL_COLOR = "white"
WALL_COLOR = "#333333"


class PongGame:
    def __init__(self, fig, ax, width: int = 10, height: int = 8):
        self.fig = fig
        self.ax = ax
        self.width = width
        self.height = height

        self._reset_state()

        # Track held keys for smooth paddle movement
        self._keys_held: set = set()
        self._key_cid = self.fig.canvas.mpl_connect(
            "key_press_event", self._on_key_press
        )
        self._keyup_cid = self.fig.canvas.mpl_connect(
            "key_release_event", self._on_key_release
        )

    # ── State ──────────────────────────────────────────────────────────────────

    def _reset_state(self) -> None:
        self.paddle_y = self.height / 2 - PADDLE_HEIGHT / 2
        self.ball_pos = [float(self.width // 2), float(self.height // 2)]
        self.ball_vel = list(BALL_INIT_VEL)
        self.score = 0
        self.game_over = False

    # ── Input ──────────────────────────────────────────────────────────────────

    def _on_key_press(self, event) -> None:
        if event.key in ("up", "down"):
            self._keys_held.add(event.key)

    def _on_key_release(self, event) -> None:
        self._keys_held.discard(event.key)

    def _apply_paddle_input(self) -> None:
        if self.game_over:
            return
        if "up" in self._keys_held:
            self.paddle_y = float(
                np.clip(self.paddle_y + PADDLE_SPEED, 0, self.height - PADDLE_HEIGHT)
            )
        if "down" in self._keys_held:
            self.paddle_y = float(
                np.clip(self.paddle_y - PADDLE_SPEED, 0, self.height - PADDLE_HEIGHT)
            )

    # ── Physics ────────────────────────────────────────────────────────────────

    def _update(self, frame) -> list:
        if self.game_over:
            self._draw()
            return []

        self._apply_paddle_input()

        self.ball_pos[0] += self.ball_vel[0]
        self.ball_pos[1] += self.ball_vel[1]

        # Top / bottom wall bounce
        if self.ball_pos[1] - BALL_RADIUS <= 0:
            self.ball_pos[1] = BALL_RADIUS
            self.ball_vel[1] = abs(self.ball_vel[1])
        elif self.ball_pos[1] + BALL_RADIUS >= self.height:
            self.ball_pos[1] = self.height - BALL_RADIUS
            self.ball_vel[1] = -abs(self.ball_vel[1])

        # Right wall bounce
        if self.ball_pos[0] + BALL_RADIUS >= self.width:
            self.ball_pos[0] = self.width - BALL_RADIUS
            self.ball_vel[0] = -abs(self.ball_vel[0])

        # Paddle collision — check overlap to prevent tunneling
        paddle_right = PADDLE_X + PADDLE_WIDTH
        ball_left = self.ball_pos[0] - BALL_RADIUS
        ball_right = self.ball_pos[0] + BALL_RADIUS

        if ball_left <= paddle_right and ball_right >= PADDLE_X:
            ball_bottom = self.ball_pos[1] - BALL_RADIUS
            ball_top = self.ball_pos[1] + BALL_RADIUS
            if (
                ball_bottom <= self.paddle_y + PADDLE_HEIGHT
                and ball_top >= self.paddle_y
            ):
                # Deflect and nudge ball out of paddle
                self.ball_pos[0] = paddle_right + BALL_RADIUS
                self.ball_vel[0] = abs(self.ball_vel[0])

                # Add slight angle variation based on where ball hits paddle
                hit_pos = (self.ball_pos[1] - self.paddle_y) / PADDLE_HEIGHT  # 0..1
                self.ball_vel[1] += (hit_pos - 0.5) * 0.1

                # Speed up gradually, cap at MAX_SPEED
                speed = np.hypot(*self.ball_vel)
                if speed < MAX_SPEED:
                    factor = min((speed + SPEED_INCREMENT) / speed, MAX_SPEED / speed)
                    self.ball_vel[0] *= factor
                    self.ball_vel[1] *= factor

                self.score += 1
                logger.debug("Paddle hit — score: %d, speed: %.3f", self.score, speed)
            else:
                self.game_over = True
                logger.debug("Ball missed paddle — game over, score: %d", self.score)

        # Ball passed paddle entirely
        elif self.ball_pos[0] < PADDLE_X - BALL_RADIUS:
            self.game_over = True

        self._draw()
        return []

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

    def _draw(self) -> None:
        self._setup_axes()

        # Centre dashed line
        for y in np.arange(0.5, self.height, 1.0):
            self.ax.plot(
                [self.width / 2, self.width / 2],
                [y, y + 0.5],
                color=WALL_COLOR,
                linewidth=1,
            )

        # Paddle
        self.ax.add_patch(
            patches.Rectangle(
                (PADDLE_X, self.paddle_y),
                PADDLE_WIDTH,
                PADDLE_HEIGHT,
                facecolor=PADDLE_COLOR,
            )
        )

        # Ball
        self.ax.add_patch(
            patches.Circle(
                self.ball_pos,
                BALL_RADIUS,
                facecolor=BALL_COLOR,
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
                f"Pong — Score: {self.score}",
                fontsize=16,
                fontweight="bold",
                color="white",
            )

    # ── Cleanup ────────────────────────────────────────────────────────────────

    def _disconnect(self) -> None:
        self.fig.canvas.mpl_disconnect(self._key_cid)
        self.fig.canvas.mpl_disconnect(self._keyup_cid)

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
