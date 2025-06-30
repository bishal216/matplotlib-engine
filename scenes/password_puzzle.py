import matplotlib.pyplot as plt
import matplotlib.patches as patches

class PasswordPuzzleGame:
    def __init__(self, fig, ax, clues, password):
        self.fig = fig
        self.ax = ax
        self.setup_plot()
        self.password = password.upper()
        self.attempts = 0
        self.max_attempts = 100
        self.current_guess = ""
        self.clues = clues
        self.state = "playing"
        self.message = ""
        self.setup_controls()

    def setup_plot(self):
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 6)
        self.ax.set_aspect('equal')
        self.ax.set_facecolor('#232946')
        self.ax.grid(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

    def setup_controls(self):
        self.fig.canvas.mpl_connect('key_press_event', self.handle_key)

    def handle_key(self, event):
        if self.state == "playing":
            if event.key == "backspace":
                self.current_guess = self.current_guess[:-1]
            elif event.key == "enter":
                self.check_password()
            elif event.key == "escape":
                self.quit_game()
            elif event.key and len(event.key) == 1 and event.key.isalpha() and len(self.current_guess) < 16:
                self.current_guess += event.key.upper()
        elif self.state in ("win", "lose"):
            if event.key == "r":
                self.reset()
            elif event.key == "escape":
                self.quit_game()
        self.draw()

    def check_password(self):
        self.attempts += 1
        if self.current_guess == self.password:
            self.state = "win"
            self.message = "Correct! You solved the password."
        elif self.attempts >= self.max_attempts:
            self.state = "lose"
            self.message = f"Out of attempts! The password was: {self.password}"
        else:
            self.message = f"Incorrect! Attempts left: {self.max_attempts - self.attempts}"
            self.current_guess = ""

    def reset(self):
        self.current_guess = ""
        self.state = "playing"
        self.message = ""
        self.attempts = 0
        self.draw()

    def quit_game(self):
        self.state = "quit"
        self.ax.clear()
        self.ax.set_facecolor('#1a1a2e')
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 8)
        self.ax.set_aspect('equal')
        self.ax.grid(False)
        self.ax.text(5, 4, "Game Closed", fontsize=30, color='white',
                     ha='center', va='center')
        self.ax.text(5, 3, "Press 'r' to restart or close window", fontsize=15,
                     color='white', ha='center', va='center')
        plt.draw()

    def draw(self):
        self.ax.clear()
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 6)
        self.ax.set_aspect('equal')
        self.ax.set_facecolor('#232946')
        self.ax.grid(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        self.ax.text(5, 5.5, "Password Puzzle", fontsize=22, fontweight='bold', ha='center', color='#eebbc3')
        self.ax.text(5, 4.7, "Clues:", fontsize=14, fontweight='bold', ha='center', color='#b8c1ec')

        for i, clue in enumerate(self.clues):
            self.ax.text(5, 4.3 - i*0.4, clue, fontsize=12, ha='center', color='#b8c1ec')

        self.ax.add_patch(patches.Rectangle((2.5, 2.2), 5, 0.7, facecolor='#121629', edgecolor='#eebbc3', linewidth=2))
        masked = '*' * len(self.current_guess)
        self.ax.text(5, 2.55, masked, fontsize=24, ha='center', color='#eebbc3')

        if self.message:
            color = '#2ecc71' if self.state == 'win' else ('#e74c3c' if self.state == 'lose' else '#eebbc3')
            self.ax.text(5, 1.5, self.message, fontsize=14, ha='center', color=color)

        if self.state == "playing":
            self.ax.text(5, 0.8, "Type your guess. Enter=Submit, Backspace=Erase, ESC=Quit", fontsize=10, ha='center', color='#b8c1ec')
        else:
            self.ax.text(5, 0.8, "R=Restart, ESC=Quit", fontsize=10, ha='center', color='#b8c1ec')

        plt.draw()

    def run(self):
        self.draw()
        while self.state not in ("win", "lose", "quit"):
            plt.pause(0.1)
