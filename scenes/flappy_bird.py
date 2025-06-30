import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
from matplotlib.animation import FuncAnimation

class FlappyBirdGame:
    def __init__(self, fig, ax, score_to_beat=100, width=10, height=8, victory_message="You win!", defeat_message="You lose!"):
        self.width = width
        self.height = height
        self.fig = fig
        self.ax = ax
        self.score_to_beat = score_to_beat

        # Game state
        self.reset_state()

        # Connect controls
        self.fig.canvas.mpl_connect('button_press_event', self.on_mouse_click)

        # For end screen event handlers connection ids
        self.end_screen_click_cid = None
        self.end_screen_key_cid = None

        # Victory and defeat messages
        self.victory_message = victory_message
        self.defeat_message = defeat_message

        self.spawn_pipe()

    def reset_state(self):
        self.bird_y = self.height // 2
        self.bird_vy = 0
        self.gravity = -0.05
        self.flap_strength = 0.25
        self.pipe_gap = 2.5
        self.pipe_width = 1
        self.pipe_speed = 0.15
        self.pipes = []
        self.score = 0
        self.game_over = False
        self.started = False
        self.paused = False

    def spawn_pipe(self):
        gap_y = random.uniform(2, self.height - 2 - self.pipe_gap)
        self.pipes.append({'x': self.width, 'gap_y': gap_y})

    def on_mouse_click(self, event):
        if self.game_over:
            return  # Ignore clicks after game over; handled in end screen
        elif not self.started:
            self.started = True
        else:
            self.flap()

    def flap(self):
        if not self.game_over and not self.paused and self.started:
            self.bird_vy = self.flap_strength

    def restart(self):
        # Disconnect end screen handlers if connected
        if self.end_screen_click_cid is not None:
            self.fig.canvas.mpl_disconnect(self.end_screen_click_cid)
            self.end_screen_click_cid = None
        if self.end_screen_key_cid is not None:
            self.fig.canvas.mpl_disconnect(self.end_screen_key_cid)
            self.end_screen_key_cid = None

        self.reset_state()
        self.spawn_pipe()
        self.ax.set_title(f'Get {self.score_to_beat} points to win! Click to Start', fontsize=16, fontweight='bold')
        plt.draw()

        # Restart animation
        if hasattr(self, 'anim'):
            self.anim.event_source.start()

    def update(self, frame):
        if self.game_over or self.paused:
            self.draw()
            return []

        if not self.started:
            self.draw(waiting=True)
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
            if pipe['x'] < 2 and pipe['x'] + self.pipe_width > 1:
                if not (pipe['gap_y'] < self.bird_y < pipe['gap_y'] + self.pipe_gap):
                    self.game_over = True

        if self.score >= self.score_to_beat:
            self.game_over = True

        self.draw()
        return []

    def clear_axes(self):
        self.ax.clear()
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.set_aspect('equal')
        self.ax.grid(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

    def draw(self, waiting=False):
        self.clear_axes()
        self.ax.set_facecolor('#87ceeb')

        for pipe in self.pipes:
            self.ax.add_patch(patches.Rectangle((pipe['x'], 0), self.pipe_width, pipe['gap_y'], facecolor='green'))
            self.ax.add_patch(patches.Rectangle(
                (pipe['x'], pipe['gap_y'] + self.pipe_gap),
                self.pipe_width,
                self.height - pipe['gap_y'] - self.pipe_gap,
                facecolor='green'))

        self.ax.add_patch(patches.Circle((1.5, self.bird_y), 0.3, facecolor='yellow', edgecolor='black'))

        if not waiting and not self.game_over:
            self.ax.text(
                self.width - 0.5, self.height - 0.5,
                f"Score: {self.score}",
                ha='right', va='top',
                fontsize=14, fontweight='bold',
                color='white',
                bbox=dict(facecolor='black', alpha=0.5, boxstyle='round,pad=0.3')
            )
        elif waiting:
            self.ax.text(
                self.width / 2, self.height / 2,
                'Click anywhere to start',
                ha='center', va='center',
                fontsize=16, fontweight='bold',
                color='black',
                bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5')
    )


    def show_end_screen(self):

        if self.score >= self.score_to_beat:
            msg = f'{self.victory_message}'
            color = 'lime'
        else:
            msg = f'{self.defeat_message}'
            color = 'red'
        self.ax.text(
                self.width / 2, self.height / 2,
                f"{msg}",
                ha='center', va='center',
                fontsize=14, fontweight='bold',
                color=f'{color}',
                bbox=dict(facecolor='black', alpha=0.5, boxstyle='round,pad=0.3')
            )

        plt.draw()

    def run(self):
        self.anim = FuncAnimation(self.fig, self.update, interval=30, blit=False, repeat=True, cache_frame_data=False)
        self.anim.event_source.start()

        while not self.game_over:
            plt.pause(0.01)

        self.anim.event_source.stop()

        self.show_end_screen()
        plt.pause(5)

        plt.show()
        return self.score

