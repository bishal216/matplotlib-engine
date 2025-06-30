import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import keyboard
import random

class TwoGuardsGame:
    def __init__(self, fig, ax):
        self.fig = fig
        self.ax = ax
        self.state = 'intro'
        self.message = ''
        self.setup_plot()
        self.setup_controls()
    def setup_plot(self):
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 8)
        self.ax.set_aspect('equal')
        self.ax.set_facecolor('#232946')
        self.ax.grid(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
    def setup_controls(self):
        keyboard.on_press_key('1', lambda _: self.choose(1))
        keyboard.on_press_key('2', lambda _: self.choose(2))
        keyboard.on_press_key('r', lambda _: self.restart())
        keyboard.on_press_key('escape', lambda _: self.quit_game())
    def choose(self, option):
        if self.state != 'intro': return
        correct = random.choice([1, 2])
        if option == correct:
            self.state = 'win'
            self.message = 'Correct! You chose the safe door.'
        else:
            self.state = 'lose'
            self.message = 'Wrong! You chose the trap door.'
        self.draw()
    def restart(self):
        self.state = 'intro'
        self.message = ''
        self.ax.set_title('Two Guards', fontsize=16, fontweight='bold')
        plt.draw()
    def quit_game(self):
        self.state = 'win'
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
        self.ax.set_ylim(0, 8)
        self.ax.set_aspect('equal')
        self.ax.set_facecolor('#232946')
        self.ax.grid(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        if self.state == 'intro':
            self.ax.set_title('Two Guards', fontsize=16, fontweight='bold')
            self.ax.text(5, 6, 'You face two doors. One leads to safety,', fontsize=14, ha='center', color='#eebbc3')
            self.ax.text(5, 5.5, 'the other to a trap. Each is guarded.', fontsize=14, ha='center', color='#eebbc3')
            self.ax.text(5, 5, 'One guard always tells the truth,', fontsize=14, ha='center', color='#eebbc3')
            self.ax.text(5, 4.5, 'the other always lies.', fontsize=14, ha='center', color='#eebbc3')
            self.ax.text(5, 3.5, 'Which door do you choose?', fontsize=14, ha='center', color='#eebbc3')
            self.ax.text(3, 2.5, 'Press 1 for Door 1', fontsize=12, ha='center', color='#b8c1ec')
            self.ax.text(7, 2.5, 'Press 2 for Door 2', fontsize=12, ha='center', color='#b8c1ec')
        elif self.state == 'win':
            self.ax.set_title('YOU WIN!', fontsize=16, fontweight='bold', color='green')
            self.ax.text(5, 4, self.message, fontsize=14, ha='center', color='#2ecc71')
            self.ax.text(5, 2, 'R: Restart | ESC: Quit', fontsize=12, ha='center', color='#b8c1ec')
        elif self.state == 'lose':
            self.ax.set_title('GAME OVER', fontsize=16, fontweight='bold', color='red')
            self.ax.text(5, 4, self.message, fontsize=14, ha='center', color='#e74c3c')
            self.ax.text(5, 2, 'R: Restart | ESC: Quit', fontsize=12, ha='center', color='#b8c1ec')
    def run(self):
        print('Two Guards Game Started!')
        print('Controls: 1/2=Choose Door, R=Restart, ESC=Quit')
        self.draw()
        while self.state not in ('win', 'lose'):
            plt.pause(0.1)

def run_two_guards_game(fig, ax):
    try:
        game = TwoGuardsGame(fig, ax)
        game.run()
    except KeyboardInterrupt:
        print('\nGame stopped by user')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    fig, ax = plt.subplots(figsize=(10, 8))
    run_two_guards_game(fig, ax) 