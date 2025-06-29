"""
Simple minigame manager for the SceneManager-based game.
"""

import importlib
import sys
from typing import Optional


class SimpleMinigameManager:
    """Simple manager for launching minigames."""
    
    def __init__(self):
        self.available_games = {
            'snake': 'minigames.snake_game',
            'minesweeper': 'minigames.minesweeper',
            'password': 'minigames.password_puzzle',
            'flappy_bird': 'minigames.flappy_bird',
            'tetris': 'minigames.tetris_game',
            'pong': 'minigames.pong_game',
            'nine_puzzle': 'minigames.nine_puzzle',
            'two_guards': 'minigames.two_guards'
        }
        
        # Map of function names for each game
        self.game_functions = {
            'snake': 'run_snake_game',
            'minesweeper': 'run_minesweeper_game',
            'password': 'run_password_puzzle',
            'flappy_bird': 'run_flappy_bird_game',
            'tetris': 'run_tetris_game',
            'pong': 'run_pong_game',
            'nine_puzzle': 'run_nine_puzzle_game',
            'two_guards': 'run_two_guards_game'
        }
        
        # Games that support shared figure/axes
        self.shared_figure_games = {
            'snake': True,
            'minesweeper': True,
            'password': True,
            'flappy_bird': True,
            'tetris': True,
            'pong': True,
            'nine_puzzle': True,
            'two_guards': True
        }
        
    def is_game_available(self, game_name: str) -> bool:
        """Check if a game is available."""
        return game_name in self.available_games
        
    def get_available_games(self) -> list:
        """Get list of available game names."""
        return list(self.available_games.keys())
        
    def supports_shared_figure(self, game_name: str) -> bool:
        """Check if a game supports shared figure/axes."""
        return self.shared_figure_games.get(game_name, False)
        
    def launch_game(self, game_name: str, fig=None, ax=None) -> bool:
        """Launch a minigame."""
        if not self.is_game_available(game_name):
            print(f"Game '{game_name}' not found.")
            return False
            
        try:
            # Import the game module
            module_name = self.available_games[game_name]
            module = importlib.import_module(module_name)
            
            # Get the function name for this game
            func_name = self.game_functions.get(game_name)
            if not func_name:
                print(f"No function mapping found for {game_name}")
                return False
                
            # Try to find and run the function
            if hasattr(module, func_name):
                func = getattr(module, func_name)
                
                # Pass figure and axes if game supports it
                if self.supports_shared_figure(game_name) and fig is not None and ax is not None:
                    func(fig, ax)
                else:
                    func()
                    
                return True
            else:
                print(f"Function {func_name} not found in {module_name}")
                return False
                
        except ImportError as e:
            print(f"Error importing {game_name}: {e}")
            return False
        except Exception as e:
            print(f"Error running {game_name}: {e}")
            return False
            
    def get_game_info(self, game_name: str) -> Optional[dict]:
        """Get information about a game."""
        if not self.is_game_available(game_name):
            return None
            
        try:
            module_name = self.available_games[game_name]
            module = importlib.import_module(module_name)
            
            func_name = self.game_functions.get(game_name, 'unknown')
            
            info = {
                'name': game_name,
                'module': module_name,
                'function': func_name,
                'description': getattr(module, '__doc__', 'No description available'),
                'has_function': hasattr(module, func_name),
                'supports_shared_figure': self.supports_shared_figure(game_name)
            }
            
            return info
            
        except ImportError:
            return None 