"""
Game Utilities Module
Reusable utilities for 2048 game development
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Tuple


class ConfigManager:
    """Manage game configuration"""
    
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Load configuration from JSON file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.get_default_config()
        return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            'game': {
                'window_width': 500,
                'window_height': 700,
                'grid_size': 4,
                'animation_duration': 0.15,
                'win_tile': 2048
            },
            'features': {
                'enable_sound': False,
                'enable_animations': True,
                'enable_leaderboard': True,
                'leaderboard_size': 20
            }
        }
    
    def get(self, key: str, default=None):
        """Get config value by key (dot notation supported)"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def set(self, key: str, value):
        """Set config value"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def save(self):
        """Save config to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)


class GameStatistics:
    """Track game statistics"""
    
    def __init__(self, filename='statistics.json'):
        self.filename = filename
        self.stats = self.load_stats()
    
    def load_stats(self) -> Dict:
        """Load statistics from file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except:
                return self.get_default_stats()
        return self.get_default_stats()
    
    def get_default_stats(self) -> Dict:
        """Get default statistics structure"""
        return {
            'total_games': 0,
            'total_moves': 0,
            'total_time_played': 0,  # seconds
            'average_score': 0.0,
            'average_moves': 0.0,
            'games_won': 0,
            'win_rate': 0.0,
            'highest_score': 0,
            'highest_tile': 0,
            'total_tiles_merged': 0,
            'play_sessions': []
        }
    
    def record_game(self, score: int, moves: int, won: bool, 
                   highest_tile: int, time_played: int, tiles_merged: int):
        """Record a completed game"""
        self.stats['total_games'] += 1
        self.stats['total_moves'] += moves
        self.stats['total_time_played'] += time_played
        self.stats['total_tiles_merged'] += tiles_merged
        
        # Update average score
        old_avg = self.stats['average_score']
        self.stats['average_score'] = (
            (old_avg * (self.stats['total_games'] - 1) + score) / 
            self.stats['total_games']
        )
        
        # Update average moves
        old_avg_moves = self.stats['average_moves']
        self.stats['average_moves'] = (
            (old_avg_moves * (self.stats['total_games'] - 1) + moves) / 
            self.stats['total_games']
        )
        
        # Update win stats
        if won:
            self.stats['games_won'] += 1
        self.stats['win_rate'] = (
            self.stats['games_won'] / self.stats['total_games'] * 100
        )
        
        # Update highest scores
        if score > self.stats['highest_score']:
            self.stats['highest_score'] = score
        if highest_tile > self.stats['highest_tile']:
            self.stats['highest_tile'] = highest_tile
        
        # Record session
        session = {
            'timestamp': datetime.now().isoformat(),
            'score': score,
            'moves': moves,
            'won': won,
            'highest_tile': highest_tile,
            'time_played': time_played
        }
        self.stats['play_sessions'].append(session)
        
        # Keep only last 100 sessions
        if len(self.stats['play_sessions']) > 100:
            self.stats['play_sessions'] = self.stats['play_sessions'][-100:]
        
        self.save()
    
    def get_summary(self) -> str:
        """Get human-readable statistics summary"""
        return f"""
        📊 Game Statistics
        ==================
        Total Games: {self.stats['total_games']}
        Games Won: {self.stats['games_won']} ({self.stats['win_rate']:.1f}%)
        Average Score: {self.stats['average_score']:.0f}
        Highest Score: {self.stats['highest_score']}
        Highest Tile: {self.stats['highest_tile']}
        Total Moves: {self.stats['total_moves']}
        Average Moves: {self.stats['average_moves']:.1f}
        Total Time: {self.format_time(self.stats['total_time_played'])}
        """
    
    @staticmethod
    def format_time(seconds: int) -> str:
        """Format seconds to human readable time"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    def save(self):
        """Save statistics to file"""
        with open(self.filename, 'w') as f:
            json.dump(self.stats, f, indent=2)


class ColorTheme:
    """Color theme management"""

    # Mobile neon palette (matches main.py Game2048UI)
    NEON_TILES = {
        0: (0.11, 0.11, 0.15, 1),
        2: (0.48, 0.17, 0.89, 1),
        4: (0.91, 0.12, 0.55, 1),
        8: (0.96, 0.77, 0.00, 1),
        16: (0.56, 0.90, 0.00, 1),
        32: (0.23, 0.11, 0.48, 1),
        64: (1.00, 0.18, 0.44, 1),
        128: (1.00, 0.54, 0.00, 1),
        256: (0.00, 0.79, 0.65, 1),
        512: (0.18, 0.61, 1.00, 1),
        1024: (1.00, 0.30, 0.60, 1),
        2048: (0.00, 0.90, 1.00, 1),
    }

    THEMES = {
        'light': {
            'background': (0.98, 0.97, 0.96, 1),
            'primary': (0.52, 0.81, 0.92, 1),
            'success': (0.70, 0.92, 0.55, 1),
            'danger': (0.92, 0.55, 0.55, 1),
            'warning': (0.93, 0.84, 0.20, 1),
            'text_primary': (0.2, 0.2, 0.2, 1),
            'text_secondary': (0.5, 0.5, 0.5, 1),
            'tiles': {
                0: (0.93, 0.93, 0.93, 1),
                2: (0.96, 0.96, 0.94, 1),
                4: (0.96, 0.96, 0.88, 1),
                8: (0.96, 0.92, 0.82, 1),
                16: (0.96, 0.89, 0.74, 1),
                32: (0.96, 0.85, 0.68, 1),
                64: (0.96, 0.81, 0.61, 1),
                128: (0.93, 0.89, 0.50, 1),
                256: (0.93, 0.88, 0.41, 1),
                512: (0.93, 0.86, 0.31, 1),
                1024: (0.93, 0.84, 0.20, 1),
                2048: (0.61, 0.85, 0.93, 1),
            }
        },
        'dark': {
            'background': (0.04, 0.04, 0.07, 1),
            'primary': (0.48, 0.17, 0.89, 1),
            'success': (0.00, 0.79, 0.65, 1),
            'danger': (1.00, 0.18, 0.44, 1),
            'warning': (0.96, 0.77, 0.00, 1),
            'text_primary': (1, 1, 1, 1),
            'text_secondary': (0.60, 0.63, 0.71, 1),
            'tiles': NEON_TILES,
        },
        'mobile': {
            'background': (0.04, 0.04, 0.07, 1),
            'primary': (0.48, 0.17, 0.89, 1),
            'success': (0.00, 0.79, 0.65, 1),
            'danger': (1.00, 0.18, 0.44, 1),
            'warning': (0.96, 0.77, 0.00, 1),
            'text_primary': (1, 1, 1, 1),
            'text_secondary': (0.60, 0.63, 0.71, 1),
            'tiles': NEON_TILES,
        },
    }
    
    @classmethod
    def get_theme(cls, name: str) -> Dict:
        """Get theme by name"""
        return cls.THEMES.get(name, cls.THEMES['mobile'])
    
    @classmethod
    def get_tile_color(cls, value: int, theme: str = 'mobile') -> Tuple:
        """Get tile color for value"""
        theme_data = cls.get_theme(theme)
        return theme_data['tiles'].get(value, (0.36, 0.42, 0.75, 1))
    
    @classmethod
    def list_themes(cls) -> List[str]:
        """List available themes"""
        return list(cls.THEMES.keys())


class ScoreValidator:
    """Validate game scores for cheating prevention"""
    
    @staticmethod
    def is_valid_score(board: List[List[int]], score: int, moves: int) -> bool:
        """Check if score is valid for given board state"""
        # Very basic validation - can be extended
        if score < 0 or moves < 0:
            return False
        
        # Check if highest tile matches board
        max_tile = max(max(row) for row in board)
        if max_tile > score:  # Can't have score less than highest tile
            return False
        
        return True
    
    @staticmethod
    def calculate_score(moves: int, highest_tile: int, won: bool) -> int:
        """Calculate expected score range"""
        base = highest_tile
        bonus = moves * 10 if won else 0
        return base + bonus


class GameExporter:
    """Export game data and replays"""
    
    @staticmethod
    def export_game_state(board: List[List[int]], score: int, moves: int, 
                         filename: str = 'game_state.json'):
        """Export current game state"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'board': board,
            'score': score,
            'moves': moves
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def import_game_state(filename: str) -> Dict:
        """Import game state from file"""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error importing game state: {e}")
            return None
    
    @staticmethod
    def export_leaderboard(scores: List[Dict], filename: str = 'leaderboard_export.csv'):
        """Export leaderboard to CSV"""
        import csv
        
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['rank', 'score', 'moves', 'timestamp'])
            writer.writeheader()
            
            for rank, score_data in enumerate(scores, 1):
                writer.writerow({
                    'rank': rank,
                    'score': score_data['score'],
                    'moves': score_data['moves'],
                    'timestamp': score_data['timestamp']
                })


class GameAnalytics:
    """Analyze game performance"""
    
    @staticmethod
    def calculate_efficiency(score: int, moves: int) -> float:
        """Calculate score per move efficiency"""
        return score / moves if moves > 0 else 0
    
    @staticmethod
    def calculate_win_probability(highest_tile: int) -> float:
        """Estimate probability of winning from current position"""
        # Simple heuristic based on highest tile
        if highest_tile >= 1024:
            return 0.8
        elif highest_tile >= 512:
            return 0.5
        elif highest_tile >= 256:
            return 0.3
        else:
            return 0.1
    
    @staticmethod
    def get_move_breakdown(board_history: List) -> Dict:
        """Analyze move patterns"""
        moves = {
            'left': 0,
            'right': 0,
            'up': 0,
            'down': 0
        }
        
        for board_state in board_history:
            move = board_state.get('move', 'unknown')
            if move in moves:
                moves[move] += 1
        
        return moves


# Convenience functions
def load_config(filename='config.json') -> Dict:
    """Quick load config"""
    manager = ConfigManager(filename)
    return manager.config


def get_statistics(filename='statistics.json') -> GameStatistics:
    """Quick get statistics"""
    return GameStatistics(filename)


def format_number(num: int) -> str:
    """Format large numbers with K, M notation"""
    if num >= 1000000:
        return f"{num / 1000000:.1f}M"
    elif num >= 1000:
        return f"{num / 1000:.1f}K"
    else:
        return str(num)


if __name__ == '__main__':
    # Example usage
    print("Game Utilities Module")
    print("Available utilities:")
    print("- ConfigManager: Manage game configuration")
    print("- GameStatistics: Track game stats")
    print("- ColorTheme: Theme management")
    print("- ScoreValidator: Validate scores")
    print("- GameExporter: Export/import game data")
    print("- GameAnalytics: Analyze game performance")
    
    # Demo
    config = load_config()
    print(f"\nGrid size: {config['game']['grid_size']}x{config['game']['grid_size']}")
