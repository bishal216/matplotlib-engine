"""
Simple input handler for the SceneManager-based game.
"""

import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton


class SimpleInputHandler:
    """Simple input handler for scene-based game."""

    def __init__(self, fig):
        self.fig = fig
        self.last_key = None
        self.mouse_clicked = False
        self.setup_callbacks()

    def setup_callbacks(self):
        """Setup matplotlib callbacks for input."""
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.fig.canvas.mpl_connect('button_press_event', self.on_mouse_click)

    def on_key_press(self, event):
        """Handle key press events."""
        self.last_key = event.key

    def on_mouse_click(self, event):
        """Handle mouse click events."""
        if event.button == MouseButton.LEFT:
            self.mouse_clicked = True

    def get_input(self):
        """Get the last input event."""
        key = self.last_key
        mouse = self.mouse_clicked

        # Reset for next frame
        self.last_key = None
        self.mouse_clicked = False

        return key, mouse

    def wait_for_input(self, timeout=None):
        """Wait for any input."""
        import time
        start_time = time.time()

        while True:
            key, mouse = self.get_input()
            if key or mouse:
                return key, mouse

            if timeout and (time.time() - start_time) > timeout:
                return None, None

            plt.pause(0.01)

    def wait_for_key(self, expected_keys=None, timeout=None):
        """Wait for a specific key press."""
        import time
        start_time = time.time()

        while True:
            key, mouse = self.get_input()
            if key:
                if expected_keys is None or key in expected_keys:
                    return key

            if timeout and (time.time() - start_time) > timeout:
                return None

            plt.pause(0.01)