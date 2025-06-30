import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

from matplotlib.animation import FuncAnimation

class PongGame:
    def __init__(self, fig, ax, width=10, height=8):
        self.width = width
        self.height = height
        self.fig = fig
        self.ax = ax
        self.paddle_height = 2
        self.paddle_y = height // 2 - self.paddle_height // 2
        self.ball_pos = [width // 2, height // 2]
        self.ball_vel = [0.15, 0.12]
        self.score = 0
        self.game_over = False
        self.paused = False
        self.setup_plot()
        self.setup_controls()

    def setup_plot(self):
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.set_aspect('equal')
        self.ax.set_facecolor('black')
        self.ax.grid(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

    def setup_controls(self):
        self.fig.canvas.mpl_connect('key_press_event', self.handle_key)

    def handle_key(self, event):
        if event.key == 'up':
            self.move_paddle(-1)
        elif event.key == 'down':
            self.move_paddle(1)

    def move_paddle(self, dy):
        if self.game_over or self.paused:
            return
        self.paddle_y = np.clip(self.paddle_y + dy, 0, self.height - self.paddle_height)

    def restart(self):
        self.paddle_y = self.height // 2 - self.paddle_height // 2
        self.ball_pos = [self.width // 2, self.height // 2]
        self.ball_vel = [0.15, 0.12]
        self.score = 0
        self.game_over = False
        self.paused = False
        self.ax.set_title(f'Pong - Score: {self.score}', fontsize=16, fontweight='bold')
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

    def update(self, frame):
        if self.game_over or self.paused:
            self.draw()
            return []
        self.ball_pos[0] += self.ball_vel[0]
        self.ball_pos[1] += self.ball_vel[1]
        if self.ball_pos[1] <= 0 or self.ball_pos[1] >= self.height:
            self.ball_vel[1] *= -1
        if self.ball_pos[0] <= 1.5:
            if self.paddle_y <= self.ball_pos[1] <= self.paddle_y + self.paddle_height:
                self.ball_vel[0] *= -1
                self.score += 1
            else:
                self.game_over = True
        if self.ball_pos[0] >= self.width:
            self.ball_vel[0] *= -1
        self.draw()
        return []

    def draw(self):
        self.ax.clear()
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.set_aspect('equal')
        self.ax.set_facecolor('black')
        self.ax.grid(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.add_patch(patches.Rectangle((1, self.paddle_y), 0.3, self.paddle_height, facecolor='white'))
        self.ax.add_patch(patches.Circle(self.ball_pos, 0.3, facecolor='white'))
        if self.game_over:
            self.ax.set_title(f'GAME OVER! Score: {self.score}\nR: Restart, ESC: Quit', fontsize=16, fontweight='bold', color='red')
        else:
            self.ax.set_title(f'Pong - Score: {self.score}', fontsize=16, fontweight='bold')

    def run(self):
        self.anim = FuncAnimation(self.fig, self.update, interval=30, blit=False, repeat=True, cache_frame_data=False)
        self.anim.event_source.start()
        while not self.game_over:
            plt.pause(0.01)
        self.anim.event_source.stop()
        return self.score
