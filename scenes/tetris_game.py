import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import random
import time
from matplotlib.animation import FuncAnimation
import keyboard

class TetrisGame:
    def __init__(self, fig, ax, width=10, height=20):
        self.width = width
        self.height = height
        self.fig = fig
        self.ax = ax
        self.board = np.zeros((height, width), dtype=int)
        self.current_piece = None
        self.current_x = 0
        self.current_y = 0
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False
        self.paused = False
        self.drop_time = 0
        self.drop_interval = 1000  # milliseconds
        
        # Tetris pieces (I, O, T, S, Z, J, L)
        self.pieces = {
            'I': {'shape': np.array([[1, 1, 1, 1]]), 'color': 'cyan'},
            'O': {'shape': np.array([[1, 1], [1, 1]]), 'color': 'yellow'},
            'T': {'shape': np.array([[0, 1, 0], [1, 1, 1]]), 'color': 'purple'},
            'S': {'shape': np.array([[0, 1, 1], [1, 1, 0]]), 'color': 'green'},
            'Z': {'shape': np.array([[1, 1, 0], [0, 1, 1]]), 'color': 'red'},
            'J': {'shape': np.array([[1, 0, 0], [1, 1, 1]]), 'color': 'blue'},
            'L': {'shape': np.array([[0, 0, 1], [1, 1, 1]]), 'color': 'orange'}
        }
        
        # Setup the plot
        self.setup_plot()
        
        # Setup keyboard controls
        self.setup_controls()
        
        # Start with a new piece
        self.new_piece()
        
    def setup_plot(self):
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.set_aspect('equal')
        self.ax.set_facecolor('black')
        self.ax.grid(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        
    def setup_controls(self):
        """Setup keyboard event handlers"""
        keyboard.on_press_key('left', lambda _: self.move_piece(-1, 0))
        keyboard.on_press_key('right', lambda _: self.move_piece(1, 0))
        keyboard.on_press_key('down', lambda _: self.move_piece(0, -1))
        keyboard.on_press_key('up', lambda _: self.rotate_piece())
        keyboard.on_press_key('space', lambda _: self.hard_drop())
        keyboard.on_press_key('p', lambda _: self.toggle_pause())
        keyboard.on_press_key('r', lambda _: self.restart())
        keyboard.on_press_key('escape', lambda _: self.quit_game())
        
    def new_piece(self):
        """Generate a new piece"""
        piece_name = random.choice(list(self.pieces.keys()))
        self.current_piece = self.pieces[piece_name]['shape']
        self.current_x = self.width // 2 - self.current_piece.shape[1] // 2
        self.current_y = self.height - 1
        
        # Check if game over
        if not self.is_valid_position(self.current_piece, self.current_x, self.current_y):
            self.game_over = True
    
    def is_valid_position(self, piece, x, y):
        """Check if piece position is valid"""
        for i in range(piece.shape[0]):
            for j in range(piece.shape[1]):
                if piece[i, j]:
                    new_x, new_y = x + j, y - i
                    if (new_x < 0 or new_x >= self.width or 
                        new_y < 0 or new_y >= self.height or 
                        self.board[new_y, new_x]):
                        return False
        return True
    
    def move_piece(self, dx, dy):
        """Move the current piece"""
        if self.game_over or self.paused:
            return
            
        new_x = self.current_x + dx
        new_y = self.current_y + dy
        
        if self.is_valid_position(self.current_piece, new_x, new_y):
            self.current_x = new_x
            self.current_y = new_y
        elif dy < 0:  # Moving down and hit something
            self.place_piece()
            self.clear_lines()
            self.new_piece()
    
    def rotate_piece(self):
        """Rotate the current piece"""
        if self.game_over or self.paused:
            return
            
        rotated = np.rot90(self.current_piece)
        if self.is_valid_position(rotated, self.current_x, self.current_y):
            self.current_piece = rotated
    
    def hard_drop(self):
        """Drop piece all the way down"""
        if self.game_over or self.paused:
            return
            
        while self.is_valid_position(self.current_piece, self.current_x, self.current_y - 1):
            self.current_y -= 1
            self.score += 2  # Bonus points for hard drop
        self.place_piece()
        self.clear_lines()
        self.new_piece()
    
    def place_piece(self):
        """Place the current piece on the board"""
        for i in range(self.current_piece.shape[0]):
            for j in range(self.current_piece.shape[1]):
                if self.current_piece[i, j]:
                    self.board[self.current_y - i, self.current_x + j] = 1
    
    def clear_lines(self):
        """Clear completed lines"""
        lines_to_clear = []
        for i in range(self.height):
            if np.all(self.board[i]):
                lines_to_clear.append(i)
        
        if lines_to_clear:
            self.board = np.delete(self.board, lines_to_clear, axis=0)
            self.board = np.vstack([np.zeros((len(lines_to_clear), self.width), dtype=int), self.board])
            
            # Update score
            lines_cleared = len(lines_to_clear)
            self.lines_cleared += lines_cleared
            self.score += lines_cleared * 100 * lines_cleared  # More points for multiple lines
    
    def toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
        if self.paused:
            self.ax.set_title(f'Tetris - PAUSED - Score: {self.score} | Lines: {self.lines_cleared}', 
                            fontsize=16, fontweight='bold', color='red')
        else:
            self.ax.set_title(f'Tetris - Score: {self.score} | Lines: {self.lines_cleared}', 
                            fontsize=16, fontweight='bold')
        plt.draw()
    
    def restart(self):
        """Restart the game"""
        self.board = np.zeros((self.height, self.width), dtype=int)
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False
        self.paused = False
        self.drop_time = 0
        self.new_piece()
        self.ax.set_title(f'Tetris - Score: {self.score} | Lines: {self.lines_cleared}', 
                        fontsize=16, fontweight='bold')
        plt.draw()
    
    def quit_game(self):
        """Quit the game and return to main menu"""
        self.game_over = True
        self.ax.clear()
        self.ax.set_facecolor('#1a1a2e')
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 8)
        self.ax.set_aspect('equal')
        self.ax.grid(False)
    
    def draw(self):
        """Draw the current game state"""
        self.ax.clear()
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.set_aspect('equal')
        self.ax.set_facecolor('black')
        self.ax.grid(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        
        if self.game_over:
            self.ax.set_title(f'GAME OVER! Final Score: {self.score}\nPress R to restart or ESC to quit', 
                            fontsize=16, fontweight='bold', color='red')
        elif self.paused:
            self.ax.set_title(f'Tetris - PAUSED - Score: {self.score} | Lines: {self.lines_cleared}', 
                            fontsize=16, fontweight='bold', color='red')
        else:
            self.ax.set_title(f'Tetris - Score: {self.score} | Lines: {self.lines_cleared}', 
                            fontsize=16, fontweight='bold')
        
        # Draw board
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y, x]:
                    rect = patches.Rectangle((x, y), 1, 1, 
                                           facecolor='gray', edgecolor='black', linewidth=1)
                    self.ax.add_patch(rect)
        
        # Draw current piece
        if self.current_piece is not None:
            piece_color = self.pieces[list(self.pieces.keys())[0]]['color']  # Default color
            for i in range(self.current_piece.shape[0]):
                for j in range(self.current_piece.shape[1]):
                    if self.current_piece[i, j]:
                        rect = patches.Rectangle((self.current_x + j, self.current_y - i), 1, 1, 
                                               facecolor='blue', edgecolor='black', linewidth=1)
                        self.ax.add_patch(rect)
        
        # Add instructions
        instructions = ("Controls:\n"
                       "Arrow Keys: Move/Rotate\n"
                       "Space: Hard Drop\n"
                       "P: Pause, R: Restart\n"
                       "ESC: Return to menu")
        self.ax.text(0.02, 0.98, instructions, transform=self.ax.transAxes,
                    fontsize=10, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    def update(self, frame):
        """Update function for animation"""
        if not self.game_over and not self.paused:
            # Auto-drop
            current_time = time.time() * 1000
            if current_time - self.drop_time > self.drop_interval:
                self.move_piece(0, -1)
                self.drop_time = current_time
        
        self.draw()
        return []
    
    def run(self):
        """Run the game"""
        print("Tetris Game Started!")
        print("Controls:")
        print("- Arrow Keys: Move/Rotate piece")
        print("- Space: Hard drop")
        print("- P: Pause/Resume")
        print("- R: Restart game")
        print("- ESC: Return to main menu")
        
        # Create animation
        self.anim = FuncAnimation(self.fig, self.update, interval=50, 
                                 blit=False, repeat=True, cache_frame_data=False)
        
        # Start animation and wait for game to end
        self.anim.event_source.start()
        while not self.game_over:
            plt.pause(0.05)
        # Stop the animation when done
        self.anim.event_source.stop()

def run_tetris_game(fig, ax):
    """Function to run the tetris game (for main menu compatibility)"""
    try:
        game = TetrisGame(fig, ax)
        game.run()
    except KeyboardInterrupt:
        print("\nGame stopped by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(10, 20))
    run_tetris_game(fig, ax) 