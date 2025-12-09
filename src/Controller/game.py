"""
VAULT - Main game module
Entry point for game modes
"""

from game_logic import run_campaign_mode, run_endless_mode, show_splash_screen

def run_game(pixel):
    """Run campaign mode"""
    return run_campaign_mode(pixel)

__all__ = ['run_game', 'run_endless_mode', 'show_splash_screen']
