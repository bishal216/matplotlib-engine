import random
import logging

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation

logger = logging.getLogger(__name__)

# ── Physics & game constants ───────────────────────────────────────────────────
GRAVITY        = -0.05
FLAP_STRENGTH  =  0.25
PIPE_GAP       =  2.5
PIPE_WIDTH     =  1.0
PIPE_SPEED     =  0.15
BIRD_X         =  1.5
BIRD_RADIUS    =  0.3
PIPE_MIN_Y     =  2.0
ANIM_INTERVAL  =  30     # ms between frames
PAUSE_INTERVAL =  0.01   # seconds between event polls

# ── Colours ────────────────────────────────────────────────────────────────────
SKY_COLOR     = "#87ceeb"
PIPE_COLOR    = "green"
BIRD_COLOR    = "yellow"
WIN_COLOR     = "lime"
LOSE_COLOR    = "red"


class FlappyBirdGame:
    def __init__(
        self,
        fig, ax,
        score_to_beat: int  = 100,
        width: int          = 10,
        height: int         = 8,
        victory_message: str = "You win!",
        defeat_message: str  = "You lose!",
    ):
        self.fig           = fig
        self.ax            = ax
        self.width         = width
        self.height        = height
        self.score_to_beat = score_to_beat
        self.victory_message = victory_message
        self.defeat_message  = defeat_message

        self._reset_state()

        # Single persistent click handler — disconnected on cleanup
        self._click_cid = self.fig.canvas.mpl_connect("button_press_event", self._on_mouse_click)

        self._spawn_pipe()

    # ── State ──────────────────────────────────────────────────────────────────

    def _reset_state(self) -> None:
        self.bird_y    = self.height // 2
        self.bird_vy   = 0.0
        self.pipes     = []
        self.score     = 0
        self.game_over = False
        self.started   = False

    def _spawn_pipe(self) -> None:
        gap_y = random.uniform(PIPE_MIN_Y, self.height - PIPE_MIN_Y - PIPE_GAP)
        self.pipes.append({"x": self.width, "gap_y": gap_y})

    # ── Input ──────────────────────────────────────────────────────────────────

    def _on_mouse_click(self, event) -> None:
        if self.game_over:
            return
        if not self.started:
            self.started = True
        else:
            self._flap()

    def _flap(self) -> None:
        if not self.game_over and self.started:
            self.bird_vy = FLAP_STRENGTH

    # ── Update ─────────────────────────────────────────────────────────────────

    def _update(self, frame) -> list:
        if self.game_over:
            self._draw()
            return []

        if not self.started:
            self._draw(waiting=True)
            return []

        # Physics
        self.bird_vy += GRAVITY
        self.bird_y  += self.bird_vy

        # Move pipes
        for pipe in self.pipes:
            pipe["x"] -= PIPE_SPEED

        # Remove off-screen pipes and score
        if self.pipes and self.pipes[0]["x"] < -PIPE_WIDTH:
            self.pipes.pop(0)
            self.score += 1
            self._spawn_pipe()

        # Collision — floor/ceiling
        if not (0 < self.bird_y < self.height):
            logger.debug("Bird out of bounds at y=%.2f", self.bird_y)
            self.game_over = True

        # Collision — pipes
        for pipe in self.pipes:
            if pipe["x"] < BIRD_X + BIRD_RADIUS and pipe["x"] + PIPE_WIDTH > BIRD_X - BIRD_RADIUS:
                in_gap = pipe["gap_y"] < self.bird_y < pipe["gap_y"] + PIPE_GAP
                if not in_gap:
                    logger.debug("Bird hit pipe at x=%.2f", pipe["x"])
                    self.game_over = True

        # Win condition
        if self.score >= self.score_to_beat:
            self.game_over = True

        self._draw()
        return []

    # ── Drawing ────────────────────────────────────────────────────────────────

    def _clear_axes(self) -> None:
        self.ax.clear()
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.set_aspect("equal")
        self.ax.set_facecolor(SKY_COLOR)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.grid(False)

    def _draw(self, waiting: bool = False) -> None:
        self._clear_axes()

        # Pipes
        for pipe in self.pipes:
            self.ax.add_patch(patches.Rectangle(
                (pipe["x"], 0), PIPE_WIDTH, pipe["gap_y"],
                facecolor=PIPE_COLOR,
            ))
            self.ax.add_patch(patches.Rectangle(
                (pipe["x"], pipe["gap_y"] + PIPE_GAP),
                PIPE_WIDTH, self.height - pipe["gap_y"] - PIPE_GAP,
                facecolor=PIPE_COLOR,
            ))

        # Bird
        self.ax.add_patch(patches.Circle(
            (BIRD_X, self.bird_y), BIRD_RADIUS,
            facecolor=BIRD_COLOR, edgecolor="black",
        ))

        # HUD
        if waiting:
            self.ax.text(
                self.width / 2, self.height / 2,
                "Click anywhere to start",
                ha="center", va="center",
                fontsize=16, fontweight="bold", color="black",
                bbox=dict(facecolor="white", alpha=0.8, boxstyle="round,pad=0.5"),
            )
        elif not self.game_over:
            self.ax.text(
                self.width - 0.5, self.height - 0.5,
                f"Score: {self.score}",
                ha="right", va="top",
                fontsize=14, fontweight="bold", color="white",
                bbox=dict(facecolor="black", alpha=0.5, boxstyle="round,pad=0.3"),
            )

    def _show_end_screen(self) -> None:
        won   = self.score >= self.score_to_beat
        msg   = self.victory_message if won else self.defeat_message
        color = WIN_COLOR if won else LOSE_COLOR

        self.ax.text(
            self.width / 2, self.height / 2, msg,
            ha="center", va="center",
            fontsize=14, fontweight="bold", color=color,
            bbox=dict(facecolor="black", alpha=0.5, boxstyle="round,pad=0.3"),
        )
        self.fig.canvas.draw_idle()

    # ── Cleanup ────────────────────────────────────────────────────────────────

    def _disconnect(self) -> None:
        self.fig.canvas.mpl_disconnect(self._click_cid)

    # ── Public API ─────────────────────────────────────────────────────────────

    def run(self) -> int:
        # cache_frame_data=False prevents a matplotlib memory leak on long runs
        self.anim = FuncAnimation(
            self.fig, self._update,
            interval=ANIM_INTERVAL, blit=False, repeat=True, cache_frame_data=False,
        )

        while not self.game_over:
            plt.pause(PAUSE_INTERVAL)

        self.anim.event_source.stop()
        self._show_end_screen()

        # Wait for click or space to dismiss end screen
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

        return self.score