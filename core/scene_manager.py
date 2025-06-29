"""
Simple Scene Manager for the Adventure Game.
Handles scene transitions and rendering based on story.json.
"""

import json
import os
from typing import Dict, Any, Optional


class SceneManager:
    """Manages scenes and transitions for the game."""
    
    def __init__(self, story_file: str = 'data/story.json'):
        self.story_file = story_file
        self.scenes: Dict[str, Any] = {}
        self.current_scene_id = 'intro'
        self.selected_option = 0
        self._loaded = False
        
    def load_story(self) -> bool:
        """Load story data from JSON file."""
        try:
            if not os.path.exists(self.story_file):
                print(f"Story file '{self.story_file}' not found.")
                return False
                
            with open(self.story_file, 'r', encoding='utf-8') as f:
                story_data = json.load(f)
                
            # Validate story structure
            if 'scenes' not in story_data:
                print("Missing 'scenes' key in story data.")
                return False
                
            self.scenes = story_data['scenes']
            self._loaded = True
            
            print(f"Successfully loaded story with {len(self.scenes)} scenes.")
            return True
            
        except json.JSONDecodeError as e:
            print(f"Error parsing story JSON: {e}")
            return False
        except Exception as e:
            print(f"Error loading story: {e}")
            return False
            
    def get_current_scene(self) -> Optional[Dict[str, Any]]:
        """Get the current scene data."""
        return self.scenes.get(self.current_scene_id)
        
    def get_scene(self, scene_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific scene by ID."""
        return self.scenes.get(scene_id)
        
    def go_to_scene(self, scene_id: str) -> bool:
        """Go to a specific scene."""
        if scene_id in self.scenes:
            self.current_scene_id = scene_id
            self.selected_option = 0
            return True
        return False
        
    def go_to_next_scene(self) -> bool:
        """Go to the next scene based on current scene's 'next' field."""
        current_scene = self.get_current_scene()
        if current_scene and 'next' in current_scene:
            return self.go_to_scene(current_scene['next'])
        return False
        
    def select_option(self, option_index: int) -> bool:
        """Select an option in a menu scene."""
        current_scene = self.get_current_scene()
        if not current_scene or current_scene.get('type') != 'menu':
            return False
            
        options = current_scene.get('options', [])
        if 0 <= option_index < len(options):
            next_scene = options[option_index].get('next')
            if next_scene:
                return self.go_to_scene(next_scene)
        return False
        
    def move_selection(self, direction: int):
        """Move the selection in menu scenes."""
        current_scene = self.get_current_scene()
        if current_scene and current_scene.get('type') == 'menu':
            options = current_scene.get('options', [])
            self.selected_option = (self.selected_option + direction) % len(options)
            
    def is_menu_scene(self) -> bool:
        """Check if current scene is a menu scene."""
        current_scene = self.get_current_scene()
        return current_scene and current_scene.get('type') == 'menu'
        
    def is_text_scene(self) -> bool:
        """Check if current scene is a text scene."""
        current_scene = self.get_current_scene()
        return current_scene and current_scene.get('type') == 'text'
        
    def is_minigame_scene(self) -> bool:
        """Check if current scene is a minigame scene."""
        current_scene = self.get_current_scene()
        return current_scene and current_scene.get('type') == 'minigame'
        
    def is_exit_scene(self) -> bool:
        """Check if current scene is an exit scene."""
        current_scene = self.get_current_scene()
        return current_scene and current_scene.get('type') == 'exit'
        
    def get_minigame_name(self) -> Optional[str]:
        """Get the minigame name from current scene."""
        current_scene = self.get_current_scene()
        if self.is_minigame_scene():
            return current_scene.get('game')
        return None
        
    def is_loaded(self) -> bool:
        """Check if story has been loaded."""
        return self._loaded 