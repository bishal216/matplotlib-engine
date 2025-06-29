"""
Simple renderer for the SceneManager-based game.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, Any


class SimpleRenderer:
    """Simple renderer for scene-based game."""
    
    def __init__(self, fig, ax):
        self.fig = fig
        self.ax = ax
        self.setup_plot()
        
    def setup_plot(self):
        """Setup the basic plot configuration."""
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 8)
        self.ax.set_aspect('equal')
        self.ax.set_facecolor('#1a1a2e')
        self.ax.grid(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        
    def clear(self):
        """Clear the current plot."""
        self.ax.clear()
        self.setup_plot()
        
    def draw_text_scene(self, scene_data: Dict[str, Any]):
        """Draw a text scene."""
        # Title
        title = scene_data.get('title', 'Scene')
        self.ax.text(5, 7, title, fontsize=24, fontweight='bold',
                    ha='center', va='center', color='#e74c3c')
        
        # Subtitle (if present)
        if 'subtitle' in scene_data:
            subtitle = scene_data['subtitle']
            self.ax.text(5, 6.5, subtitle, fontsize=16,
                        ha='center', va='center', color='#bdc3c7')
        
        # Content
        content = scene_data.get('content', [])
        for i, line in enumerate(content):
            y_pos = 5.5 - i * 0.4
            color = '#e74c3c' if i == len(content) - 1 else '#ecf0f1'
            self.ax.text(5, y_pos, line, fontsize=12, ha='center', va='center', color=color)
        
        # Instructions
        self.ax.text(5, 0.5, "Click anywhere to continue", fontsize=10,
                    ha='center', va='center', color='#95a5a6')
        
    def draw_menu_scene(self, scene_data: Dict[str, Any], selected_option: int):
        """Draw a menu scene."""
        # Title
        title = scene_data.get('title', 'Menu')
        self.ax.text(5, 7, title, fontsize=24, fontweight='bold',
                    ha='center', va='center', color='#e74c3c')
        
        # Options
        options = scene_data.get('options', [])
        for i, option in enumerate(options):
            y_pos = 5.5 - i * 0.8
            color = '#e74c3c' if i == selected_option else '#ecf0f1'
            
            # Selection indicator
            if i == selected_option:
                self.ax.text(3.5, y_pos, ">", fontsize=16, ha='center', va='center', color=color)
            
            self.ax.text(4, y_pos, option['text'], fontsize=14, ha='left', va='center', color=color)
        
        # Instructions
        self.ax.text(5, 0.5, "Use arrow keys to navigate, Enter to select", fontsize=10,
                    ha='center', va='center', color='#95a5a6')
        
    def draw_minigame_scene(self, scene_data: Dict[str, Any]):
        """Draw a minigame scene."""
        game_name = scene_data.get('game', 'Unknown Game')
        
        # Title
        self.ax.text(5, 7, f"Loading {game_name.title()}...", fontsize=24, fontweight='bold',
                    ha='center', va='center', color='#e74c3c')
        
        # Instructions
        self.ax.text(5, 4, "The game will start in a moment.", fontsize=16,
                    ha='center', va='center', color='#ecf0f1')
        
        self.ax.text(5, 0.5, "Press any key to continue", fontsize=10,
                    ha='center', va='center', color='#95a5a6')
        
    def show(self):
        """Show the current plot."""
        plt.draw()
        plt.pause(0.01) 