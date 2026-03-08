import random
import logging

import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────
PAUSE_INTERVAL = 0.05  # seconds between event polls

# Colours
BG_COLOR = "#232946"
ACCENT_COLOR = "#eebbc3"
TEXT_COLOR = "#b8c1ec"
WIN_COLOR = "#2ecc71"
LOSE_COLOR = "#e74c3c"

# ── Riddle text ────────────────────────────────────────────────────────────────
INTRO_LINES = [
    "Two guards stand before two doors.",
    "One door leads to FREEDOM, the other to DOOM.",
    "One guard always tells the TRUTH.",
    "The other always LIES.",
    "You may ask ONE guard ONE question.",
    "",
    "The classic question to ask:",
    '"Which door would the OTHER guard say leads to freedom?"',
    "",
    "Then choose the OPPOSITE door.",
]

QUESTION = (
    'You ask Guard {guard}: "Which door would the other guard\n'
    'say leads to freedom?"'
)

GUARD_ANSWER = "Guard {guard} points to Door {door}."

HINT = "Remember: always choose the OPPOSITE of what you're told."


class TwoGuardsGame:
    def __init__(self, fig, ax):
        self.fig = fig
        self.ax = ax

        self._reset_state()
        self._key_cid = self.fig.canvas.mpl_connect("key_press_event", self._on_key)

    # ── State ──────────────────────────────────────────────────────────────────

    def _reset_state(self) -> None:
        # Randomise which guard is truthful and which door is safe
        self.safe_door = random.choice([1, 2])
        self.truth_guard = random.choice([1, 2])
        self.liar_guard = 2 if self.truth_guard == 1 else 1

        # Which guard the player chose to ask (set during ask phase)
        self.asked_guard = None
        self.guard_answer = None  # door the asked guard points to

        # State machine: "intro" → "ask" → "choose" → "win"/"lose"
        self.state = "intro"
        self.message = ""

        logger.debug(
            "New game — safe door: %d, truth guard: %d",
            self.safe_door,
            self.truth_guard,
        )

    # ── Riddle logic ───────────────────────────────────────────────────────────

    def _guard_points_to(self, asked: int) -> int:
        """
        Simulate the classic Two Guards answer.

        The truthful guard correctly reports what the liar would say.
        The liar incorrectly reports what the truthful guard would say.
        Both always end up pointing to the TRAP door — so the player
        should always pick the OTHER door.
        """
        trap_door = 2 if self.safe_door == 1 else 1

        if asked == self.truth_guard:
            # Truth-teller honestly reports what the liar would say.
            # The liar would point to the trap door (lying about freedom).
            return trap_door
        else:
            # Liar misreports what the truth-teller would say.
            # The truth-teller would point to the safe door,
            # so the liar points to the trap door.
            return trap_door

    def _ask_guard(self, guard: int) -> None:
        if self.state != "ask":
            return
        self.asked_guard = guard
        self.guard_answer = self._guard_points_to(guard)
        self.state = "choose"
        logger.debug("Asked guard %d — pointed to door %d", guard, self.guard_answer)
        self._draw()

    def _choose_door(self, door: int) -> None:
        if self.state != "choose":
            return
        if door == self.safe_door:
            self.state = "win"
            self.message = f"Door {door} leads to FREEDOM! You escape!"
        else:
            self.state = "lose"
            self.message = f"Door {door} leads to DOOM! You are trapped!"
        logger.debug(
            "Player chose door %d — safe was %d — result: %s",
            door,
            self.safe_door,
            self.state,
        )
        self._draw()

    # ── Input ──────────────────────────────────────────────────────────────────

    def _on_key(self, event) -> None:
        key = event.key

        if self.state == "intro" and key == " ":
            self.state = "ask"
            self._draw()

        elif self.state == "ask":
            if key == "1":
                self._ask_guard(1)
            elif key == "2":
                self._ask_guard(2)

        elif self.state == "choose":
            if key == "1":
                self._choose_door(1)
            elif key == "2":
                self._choose_door(2)

    # ── Drawing ────────────────────────────────────────────────────────────────

    def _setup_axes(self) -> None:
        self.ax.clear()
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 8)
        self.ax.set_aspect("equal")
        self.ax.set_facecolor(BG_COLOR)
        self.ax.grid(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

    def _draw(self) -> None:
        self._setup_axes()

        if self.state == "intro":
            self._draw_intro()
        elif self.state == "ask":
            self._draw_ask()
        elif self.state == "choose":
            self._draw_choose()
        elif self.state in ("win", "lose"):
            self._draw_end()

        self.fig.canvas.draw_idle()

    def _draw_intro(self) -> None:
        self.ax.set_title(
            "The Two Guards", fontsize=18, fontweight="bold", color=ACCENT_COLOR
        )
        for i, line in enumerate(INTRO_LINES):
            self.ax.text(
                5,
                7.2 - i * 0.55,
                line,
                fontsize=11,
                ha="center",
                color=ACCENT_COLOR if line.startswith('"') else TEXT_COLOR,
            )
        self.ax.text(
            5,
            0.4,
            "Press SPACE to begin",
            fontsize=12,
            ha="center",
            color=ACCENT_COLOR,
            bbox=dict(
                facecolor=BG_COLOR, edgecolor=ACCENT_COLOR, boxstyle="round,pad=0.4"
            ),
        )

    def _draw_ask(self) -> None:
        self.ax.set_title(
            "Choose a guard to ask", fontsize=16, fontweight="bold", color=ACCENT_COLOR
        )
        self.ax.text(
            5, 6.5, "You may ask ONE guard:", fontsize=13, ha="center", color=TEXT_COLOR
        )
        self.ax.text(
            5,
            5.8,
            '"Which door would the OTHER guard say leads to freedom?"',
            fontsize=11,
            ha="center",
            color=ACCENT_COLOR,
            style="italic",
        )
        self.ax.text(
            3,
            3.5,
            "Guard 1",
            fontsize=16,
            ha="center",
            color=TEXT_COLOR,
            fontweight="bold",
        )
        self.ax.text(
            7,
            3.5,
            "Guard 2",
            fontsize=16,
            ha="center",
            color=TEXT_COLOR,
            fontweight="bold",
        )
        self.ax.text(
            3, 2.8, "Press 1 to ask", fontsize=11, ha="center", color=ACCENT_COLOR
        )
        self.ax.text(
            7, 2.8, "Press 2 to ask", fontsize=11, ha="center", color=ACCENT_COLOR
        )

    def _draw_choose(self) -> None:
        self.ax.set_title(
            "Now choose your door", fontsize=16, fontweight="bold", color=ACCENT_COLOR
        )

        question = QUESTION.format(guard=self.asked_guard)
        answer = GUARD_ANSWER.format(guard=self.asked_guard, door=self.guard_answer)

        for i, line in enumerate(question.split("\n")):
            self.ax.text(
                5, 7.0 - i * 0.6, line, fontsize=12, ha="center", color=TEXT_COLOR
            )

        self.ax.text(
            5,
            5.5,
            answer,
            fontsize=13,
            ha="center",
            color=ACCENT_COLOR,
            fontweight="bold",
        )
        self.ax.text(
            5, 4.6, HINT, fontsize=11, ha="center", color=TEXT_COLOR, style="italic"
        )

        self.ax.text(
            3,
            3.0,
            "Door 1",
            fontsize=16,
            ha="center",
            color=TEXT_COLOR,
            fontweight="bold",
        )
        self.ax.text(
            7,
            3.0,
            "Door 2",
            fontsize=16,
            ha="center",
            color=TEXT_COLOR,
            fontweight="bold",
        )
        self.ax.text(3, 2.3, "Press 1", fontsize=11, ha="center", color=ACCENT_COLOR)
        self.ax.text(7, 2.3, "Press 2", fontsize=11, ha="center", color=ACCENT_COLOR)

    def _draw_end(self) -> None:
        won = self.state == "win"
        color = WIN_COLOR if won else LOSE_COLOR
        title = "YOU ESCAPE!" if won else "DOOM AWAITS!"

        self.ax.set_title(title, fontsize=20, fontweight="bold", color=color)
        self.ax.text(5, 5.5, self.message, fontsize=14, ha="center", color=color)

        # Reveal the truth
        self.ax.text(
            5,
            4.2,
            f"The safe door was Door {self.safe_door}.",
            fontsize=12,
            ha="center",
            color=TEXT_COLOR,
        )
        self.ax.text(
            5,
            3.5,
            f"Guard {self.truth_guard} was the truth-teller.",
            fontsize=12,
            ha="center",
            color=TEXT_COLOR,
        )
        self.ax.text(
            5,
            2.0,
            "Press space or click to continue",
            fontsize=11,
            ha="center",
            color=ACCENT_COLOR,
        )

    # ── Cleanup ────────────────────────────────────────────────────────────────

    def _disconnect(self) -> None:
        self.fig.canvas.mpl_disconnect(self._key_cid)

    # ── Public API ─────────────────────────────────────────────────────────────

    def run(self) -> None:
        self._draw()

        # Run until win or lose
        while self.state not in ("win", "lose"):
            plt.pause(PAUSE_INTERVAL)

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
