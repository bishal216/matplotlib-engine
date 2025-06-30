import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
import keyboard
from matplotlib.animation import FuncAnimation

class FlappyBirdGame:
    def __init__(self, fig, ax, width=10, height=8):
        self.width = width
        self.height = height
        self.fig = fig
        self.ax = ax
        self.bird_y = height // 2
        self.bird_vy = 0
        self.gravity = 0.3
        self.flap_strength = -2.5
        self.pipes = []
        self.pipe_gap = 2.5
        self.pipe_width = 1
        self.pipe_speed = 0.15
        self.score = 0
        self.game_over = False
        self.paused = False
        self.setup_plot()
        self.setup_controls()
        self.spawn_pipe()
    def setup_plot(self):
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.set_aspect('equal')
        self.ax.set_facecolor('#87ceeb')
        self.ax.grid(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
    def setup_controls(self):
        keyboard.on_press_key('space', lambda _: self.flap())
        keyboard.on_press_key('r', lambda _: self.restart())
        keyboard.on_press_key('escape', lambda _: self.quit_game())
    def flap(self):
        if not self.game_over and not self.paused:
            self.bird_vy = self.flap_strength
    def restart(self):
        self.bird_y = self.height // 2
        self.bird_vy = 0
        self.pipes = []
        self.score = 0
        self.game_over = False
        self.paused = False
        self.spawn_pipe()
        self.ax.set_title(f'Flappy Bird - Score: {self.score}', fontsize=16, fontweight='bold')
        plt.draw()
    def quit_game(self):
        self.game_over = True
        self.ax.clear()
        self.ax.set_facecolor('#1a1a2e')
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 8)
        self.ax.set_aspect('equal')
        self.ax.grid(False)
    def spawn_pipe(self):
        gap_y = random.uniform(2, self.height - 2 - self.pipe_gap)
        self.pipes.append({'x': self.width, 'gap_y': gap_y})
    def update(self, frame):
        if self.game_over or self.paused:
            self.draw()
            return []
        self.bird_vy += self.gravity
        self.bird_y += self.bird_vy
        for pipe in self.pipes:
            pipe['x'] -= self.pipe_speed
        if self.pipes and self.pipes[0]['x'] < -self.pipe_width:
            self.pipes.pop(0)
            self.score += 1
            self.spawn_pipe()
        if self.bird_y < 0 or self.bird_y > self.height:
            self.game_over = True
        for pipe in self.pipes:
            if (pipe['x'] < 2 and pipe['x'] + self.pipe_width > 1):
                if not (pipe['gap_y'] < self.bird_y < pipe['gap_y'] + self.pipe_gap):
                    self.game_over = True
        self.draw()
        return []
    def draw(self):
        self.ax.clear()
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.set_aspect('equal')
        self.ax.set_facecolor('#87ceeb')
        self.ax.grid(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for pipe in self.pipes:
            self.ax.add_patch(patches.Rectangle((pipe['x'], 0), self.pipe_width, pipe['gap_y'], facecolor='green'))
            self.ax.add_patch(patches.Rectangle((pipe['x'], pipe['gap_y'] + self.pipe_gap), self.pipe_width, self.height - pipe['gap_y'] - self.pipe_gap, facecolor='green'))
        self.ax.add_patch(patches.Circle((1.5, self.bird_y), 0.3, facecolor='yellow', edgecolor='black'))
        if self.game_over:
            self.ax.set_title(f'GAME OVER! Score: {self.score}\nR: Restart, ESC: Quit', fontsize=16, fontweight='bold', color='red')
        else:
            self.ax.set_title(f'Flappy Bird - Score: {self.score}', fontsize=16, fontweight='bold')
        self.ax.text(0.5, 0.1, 'Space: Flap | R: Restart | ESC: Quit', transform=self.ax.transAxes, fontsize=10, color='black')
    def run(self):
        print('Flappy Bird Game Started!')
        print('Controls: Space=Flap, R=Restart, ESC=Quit')
        self.anim = FuncAnimation(self.fig, self.update, interval=30, blit=False, repeat=True, cache_frame_data=False)
        self.anim.event_source.start()
        while not self.game_over:
            plt.pause(0.01)
        self.anim.event_source.stop()

def run_flappy_bird_game(fig, ax):
    try:
        game = FlappyBirdGame(fig, ax)
        game.run()
    except KeyboardInterrupt:
        print('\nGame stopped by user')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 8))
    run_flappy_bird_game(fig, ax)