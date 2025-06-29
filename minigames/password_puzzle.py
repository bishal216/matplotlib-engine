import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import keyboard

class PasswordPuzzle:
    def __init__(self, fig, ax):
        self.fig = fig
        self.ax = ax
        self.setup_plot()
        self.password = "PYTHON"
        self.attempts = 0
        self.max_attempts = 3
        self.current_guess = ""
        self.clues = [
            "I am a programming language",
            "I am named after a snake",
            "I am popular for data science",
            "I have simple syntax",
            "I was created by Guido van Rossum"
        ]
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
        keyboard.on_press(self.handle_key)
    def handle_key(self, e):
        if self.state == "playing":
            if e.name == "backspace":
                self.current_guess = self.current_guess[:-1]
            elif e.name == "enter":
                self.check_password()
            elif e.name == "esc":
                self.quit_game()
            elif len(e.name) == 1 and len(self.current_guess) < 16:
                self.current_guess += e.name.upper()
        elif self.state in ("win", "lose"):
            if e.name == "r":
                self.reset()
            elif e.name == "esc":
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
    def run(self):
        print("\n=== Password Puzzle ===")
        print("Clues:")
        for clue in self.clues:
            print(clue)
        print("Type your guess in the window.")
        self.draw()
        while self.state != "quit":
            plt.pause(0.1)

def run_password_puzzle(fig, ax):
    try:
        game = PasswordPuzzle(fig, ax)
        game.run()
    except KeyboardInterrupt:
        print("\nGame stopped by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 6))
    run_password_puzzle(fig, ax) 