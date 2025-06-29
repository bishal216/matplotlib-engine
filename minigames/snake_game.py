import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import random
import time
from matplotlib.animation import FuncAnimation
import keyboard

class SnakeGame:
    def __init__(self, fig=None, ax=None, width=20, height=20):
        self.width = width
        self.height = height
        self.snake = [(width//2, height//2)]  # Start at center
        self.direction = [1, 0]  # Start moving right
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.paused = False
        
        # Use provided figure and axes, or create new ones
        if fig is not None and ax is not None:
            self.fig = fig
            self.ax = ax
            self.own_figure = False
        else:
            self.fig, self.ax = plt.subplots(figsize=(10, 8))
            self.own_figure = True
            
        self.setup_plot()
        
        # Setup keyboard controls
        self.setup_controls()
        
    def setup_plot(self):
        """Setup the plot configuration"""
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.set_aspect('equal')
        self.ax.set_title(f'Snake Game - Score: {self.score}', fontsize=16, fontweight='bold')
        self.ax.grid(True, alpha=0.3)
        
        # Remove axis labels and ticks
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        
    def setup_controls(self):
        """Setup keyboard event handlers"""
        keyboard.on_press_key('up', lambda _: self.change_direction([0, 1]))
        keyboard.on_press_key('down', lambda _: self.change_direction([0, -1]))
        keyboard.on_press_key('left', lambda _: self.change_direction([-1, 0]))
        keyboard.on_press_key('right', lambda _: self.change_direction([1, 0]))
        keyboard.on_press_key('space', lambda _: self.toggle_pause())
        keyboard.on_press_key('r', lambda _: self.restart())
        keyboard.on_press_key('escape', lambda _: self.quit_game())
        
    def change_direction(self, new_direction):
        """Change snake direction (prevent 180-degree turns)"""
        if not self.paused and not self.game_over:
            # Prevent moving in opposite direction
            if (new_direction[0] != -self.direction[0] or 
                new_direction[1] != -self.direction[1]):
                self.direction = new_direction
    
    def toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
        if self.paused:
            self.ax.set_title(f'Snake Game - PAUSED - Score: {self.score}', 
                            fontsize=16, fontweight='bold', color='red')
        else:
            self.ax.set_title(f'Snake Game - Score: {self.score}', 
                            fontsize=16, fontweight='bold')
        plt.draw()
    
    def restart(self):
        """Restart the game"""
        self.snake = [(self.width//2, self.height//2)]
        self.direction = [1, 0]
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.paused = False
        self.ax.set_title(f'Snake Game - Score: {self.score}', 
                        fontsize=16, fontweight='bold')
        plt.draw()
    
    def quit_game(self):
        """Quit the game and return to main menu"""
        self.game_over = True
        # Clear the axes for return to main game
        self.ax.clear()
        self.ax.set_facecolor('#1a1a2e')
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 8)
        self.ax.set_aspect('equal')
        self.ax.grid(False)
    
    def generate_food(self):
        """Generate food at random position (not on snake)"""
        while True:
            food = (random.randint(0, self.width-1), 
                   random.randint(0, self.height-1))
            if food not in self.snake:
                return food
    
    def move_snake(self):
        """Move the snake and check for collisions"""
        if self.game_over or self.paused:
            return
        
        # Calculate new head position
        new_head = (self.snake[0][0] + self.direction[0],
                   self.snake[0][1] + self.direction[1])
        
        # Check for wall collision
        if (new_head[0] < 0 or new_head[0] >= self.width or
            new_head[1] < 0 or new_head[1] >= self.height):
            self.game_over = True
            return
        
        # Check for self collision
        if new_head in self.snake:
            self.game_over = True
            return
        
        # Add new head
        self.snake.insert(0, new_head)
        
        # Check if food is eaten
        if new_head == self.food:
            self.score += 10
            self.food = self.generate_food()
            self.ax.set_title(f'Snake Game - Score: {self.score}', 
                            fontsize=16, fontweight='bold')
        else:
            # Remove tail if no food eaten
            self.snake.pop()
    
    def draw(self):
        """Draw the current game state"""
        self.ax.clear()
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        
        if self.game_over:
            self.ax.set_title(f'GAME OVER! Final Score: {self.score}\nPress R to restart or ESC to quit', 
                            fontsize=16, fontweight='bold', color='red')
        elif self.paused:
            self.ax.set_title(f'Snake Game - PAUSED - Score: {self.score}', 
                            fontsize=16, fontweight='bold', color='red')
        else:
            self.ax.set_title(f'Snake Game - Score: {self.score}', 
                            fontsize=16, fontweight='bold')
        
        # Draw snake
        for i, segment in enumerate(self.snake):
            color = 'darkgreen' if i == 0 else 'green'  # Head is darker
            rect = patches.Rectangle(segment, 1, 1, 
                                   facecolor=color, edgecolor='black', linewidth=1)
            self.ax.add_patch(rect)
        
        # Draw food
        food_rect = patches.Rectangle(self.food, 1, 1, 
                                    facecolor='red', edgecolor='black', linewidth=1)
        self.ax.add_patch(food_rect)
        
        # Add instructions
        instructions = ("Controls: Arrow Keys to move\n"
                       "Space to pause, R to restart\n"
                       "ESC to return to menu")
        self.ax.text(0.02, 0.98, instructions, transform=self.ax.transAxes,
                    fontsize=10, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    def update(self, frame):
        """Update function for animation"""
        self.move_snake()
        self.draw()
        return []
    
    def run(self):
        """Run the game"""
        print("Snake Game Started!")
        print("Controls:")
        print("- Arrow Keys: Move snake")
        print("- Space: Pause/Resume")
        print("- R: Restart game")
        print("- ESC: Return to main menu")
        
        # Create animation
        self.anim = FuncAnimation(self.fig, self.update, interval=200, 
                                 blit=False, repeat=True, cache_frame_data=False)
        
        # Only call plt.show() if we own the figure
        if self.own_figure:
            plt.show()
        else:
            # For shared figures, just start the animation and wait for ESC
            self.anim.event_source.start()
            # Wait for the game to end (ESC pressed)
            while not self.game_over:
                plt.pause(0.1)
            # Stop the animation when done
            self.anim.event_source.stop()

def run_snake_game(fig=None, ax=None):
    """Function to run the snake game (for main menu compatibility)"""
    try:
        game = SnakeGame(fig, ax)
        game.run()
    except KeyboardInterrupt:
        print("\nGame stopped by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_snake_game() 