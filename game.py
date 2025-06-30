"""
Simple Adventure Game using SceneManager.
"""

import matplotlib.pyplot as plt
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.scene_manager import SceneManager
from ui.simple_renderer import SimpleRenderer
from ui.simple_input import SimpleInputHandler
from minigames.simple_minigame_manager import SimpleMinigameManager


class SimpleAdventureGame:
    """Simple adventure game using SceneManager."""

    def __init__(self):
        self.scene_manager = SceneManager()
        self.minigame_manager = SimpleMinigameManager()

        # Setup matplotlib
        plt.ion()  # Interactive mode
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.fig.canvas.manager.set_window_title('Bishwash Adventures')

        # Setup renderer and input handler
        self.renderer = SimpleRenderer(self.fig, self.ax)
        self.input_handler = SimpleInputHandler(self.fig)

        # Setup figure close event handler
        self.fig.canvas.mpl_connect('close_event', self.on_figure_close)
        self.figure_closed = False

        self.running = False

    def on_figure_close(self, event):
        """Handle figure close event."""
        print("Game window was closed by user.")
        self.figure_closed = True
        self.running = False

    def initialize(self) -> bool:
        """Initialize the game."""
        print("Initializing Simple Adventure Game...")

        # Load story
        if not self.scene_manager.load_story():
            print("Failed to load story data.")
            return False

        print("Game initialized successfully!")
        return True

    def is_figure_closed(self) -> bool:
        """Check if the figure has been closed by the user."""
        if self.figure_closed:
            return True
        try:
            # Try to access the figure's canvas
            _ = self.fig.canvas
            return False
        except AttributeError:
            return True

    def run(self):
        """Run the main game loop."""
        if not self.initialize():
            return

        self.running = True
        print("Starting game loop...")

        while self.running:
            # Check if figure was closed by user
            if self.is_figure_closed():
                print("Game window was closed by user.")
                self.running = False
                break

            self.update()
            self.render()

        self.cleanup()

    def update(self):
        """Update game state."""
        # Handle input
        key, mouse = self.input_handler.get_input()

        if self.scene_manager.is_exit_scene():
            self.running = False
            return

        if self.scene_manager.is_text_scene():
            # Text scenes advance on any input
            if key or mouse:
                self.scene_manager.go_to_next_scene()

        elif self.scene_manager.is_menu_scene():
            # Menu scenes handle navigation
            if key == 'up':
                self.scene_manager.move_selection(-1)
            elif key == 'down':
                self.scene_manager.move_selection(1)
            elif key == 'enter':
                self.scene_manager.select_option(self.scene_manager.selected_option)

        elif self.scene_manager.is_minigame_scene():
            # Minigame scenes - launch the game and wait for it to complete
            game_name = self.scene_manager.get_minigame_name()
            if game_name:
                print(f"Launching {game_name}...")

                # Launch minigame with shared figure if supported
                success = self.minigame_manager.launch_game(game_name, self.fig, self.ax)

                if success:
                    print(f"{game_name} completed successfully!")
                else:
                    print(f"Failed to run {game_name}")

            # Go to next scene after minigame (regardless of success/failure)
            self.scene_manager.go_to_next_scene()

    def render(self):
        """Render the current scene."""
        # Check if figure is still valid before rendering
        if self.is_figure_closed():
            return

        self.renderer.clear()

        current_scene = self.scene_manager.get_current_scene()
        if not current_scene:
            return

        scene_type = current_scene.get('type', 'text')

        if scene_type == 'text':
            self.renderer.draw_text_scene(current_scene)
        elif scene_type == 'menu':
            self.renderer.draw_menu_scene(current_scene, self.scene_manager.selected_option)
        elif scene_type == 'minigame':
            self.renderer.draw_minigame_scene(current_scene)
        elif scene_type == 'exit':
            # Exit scene - just show a message
            self.ax.text(5, 4, "Thanks for playing!", fontsize=24, fontweight='bold',
                        ha='center', va='center', color='#e74c3c')

        self.renderer.show()

    def cleanup(self):
        """Clean up resources."""
        print("Cleaning up...")
        try:
            plt.close('all')
        except Exception as e:
            print(f"Error closing figures: {e}")
            pass
        print("Game ended.")


def main():
    """Main entry point."""
    game = SimpleAdventureGame()
    try:
        game.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
    except Exception as e:
        print(f"Error running game: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()