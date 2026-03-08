import logging

import matplotlib.pyplot as plt
import matplotlib.patches as patches

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────
PAUSE_INTERVAL = 0.05  # seconds between event polls
MAX_GUESS_LEN = 16
DEFAULT_ATTEMPTS = 10

# Colours
BG_COLOR = "#232946"
ACCENT_COLOR = "#eebbc3"
TEXT_COLOR = "#b8c1ec"
INPUT_BG = "#121629"
WIN_COLOR = "#2ecc71"
LOSE_COLOR = "#e74c3c"


class PasswordPuzzleGame:
    def __init__(
        self, fig, ax, clues: list, password: str, max_attempts: int = DEFAULT_ATTEMPTS
    ):
        self.fig = fig
        self.ax = ax
        self.clues = clues
        self.password = password.upper()
        self.max_attempts = max_attempts

        self.current_guess = ""
        self.attempts = 0
        self.state = "playing"  # "playing" | "win" | "lose"
        self.message = ""

        self._key_cid = self.fig.canvas.mpl_connect("key_press_event", self._handle_key)

    # ── Input ──────────────────────────────────────────────────────────────────

    def _handle_key(self, event) -> None:
        if self.state != "playing":
            return

        key = event.key or ""

        if key == "backspace":
            self.current_guess = self.current_guess[:-1]

        elif key == "enter":
            self._check_password()

        elif (
            len(key) == 1
            and (key.isalpha() or key.isdigit())
            and len(self.current_guess) < MAX_GUESS_LEN
        ):
            self.current_guess += key.upper()

        self._draw()

    # ── Game logic ─────────────────────────────────────────────────────────────

    def _check_password(self) -> None:
        if not self.current_guess:
            return

        self.attempts += 1

        if self.current_guess == self.password:
            self.state = "win"
            self.message = "Correct! You solved the puzzle."
            logger.debug("Password solved in %d attempts", self.attempts)

        elif self.attempts >= self.max_attempts:
            self.state = "lose"
            self.message = f"Out of attempts! The password was: {self.password}"
            logger.debug("Password puzzle failed after %d attempts", self.attempts)

        else:
            remaining = self.max_attempts - self.attempts
            self.message = (
                f"Incorrect! {remaining} attempt{'s' if remaining != 1 else ''} left"
            )
            self.current_guess = ""

    # ── Drawing ────────────────────────────────────────────────────────────────

    def _setup_axes(self) -> None:
        self.ax.clear()
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 6)
        self.ax.set_aspect("equal")
        self.ax.set_facecolor(BG_COLOR)
        self.ax.grid(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

    def _draw(self) -> None:
        self._setup_axes()

        # Title
        self.ax.text(
            5,
            5.5,
            "Password Puzzle",
            fontsize=22,
            fontweight="bold",
            ha="center",
            color=ACCENT_COLOR,
        )

        # Clues
        self.ax.text(
            5,
            4.7,
            "Clues:",
            fontsize=14,
            fontweight="bold",
            ha="center",
            color=TEXT_COLOR,
        )
        for i, clue in enumerate(self.clues):
            self.ax.text(
                5, 4.3 - i * 0.4, clue, fontsize=12, ha="center", color=TEXT_COLOR
            )

        # Attempt counter
        self.ax.text(
            9.5,
            5.7,
            f"{self.attempts}/{self.max_attempts}",
            fontsize=11,
            ha="right",
            va="top",
            color=TEXT_COLOR,
        )

        # Input box
        self.ax.add_patch(
            patches.Rectangle(
                (2.5, 2.2),
                5,
                0.7,
                facecolor=INPUT_BG,
                edgecolor=ACCENT_COLOR,
                linewidth=2,
            )
        )
        masked = "•" * len(self.current_guess)
        self.ax.text(5, 2.55, masked, fontsize=24, ha="center", color=ACCENT_COLOR)

        # Feedback message
        if self.message:
            if self.state == "win":
                msg_color = WIN_COLOR
            elif self.state == "lose":
                msg_color = LOSE_COLOR
            else:
                msg_color = ACCENT_COLOR
            self.ax.text(
                5, 1.5, self.message, fontsize=14, ha="center", color=msg_color
            )

        # Instructions
        if self.state == "playing":
            self.ax.text(
                5,
                0.8,
                "Type your guess   Enter = Submit   Backspace = Erase",
                fontsize=10,
                ha="center",
                color=TEXT_COLOR,
            )
        else:
            self.ax.text(
                5,
                0.8,
                "Press space or click to continue",
                fontsize=10,
                ha="center",
                color=TEXT_COLOR,
            )

        self.fig.canvas.draw_idle()

    # ── Cleanup ────────────────────────────────────────────────────────────────

    def _disconnect(self) -> None:
        self.fig.canvas.mpl_disconnect(self._key_cid)

    # ── Public API ─────────────────────────────────────────────────────────────

    def run(self) -> None:
        self._draw()

        while self.state == "playing":
            plt.pause(PAUSE_INTERVAL)

        # Show final state then wait for dismissal
        self._draw()

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
