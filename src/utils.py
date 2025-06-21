import pygame
import config
from ui import display_text, draw_health_bar

def load_image(file_path):
    """Load an image from the specified file path."""
    image = pygame.image.load(file_path)
    return image

def manage_game_settings(settings):
    """Manage game settings such as volume, difficulty, etc."""
    # Placeholder for managing game settings
    pass

def add_to_log(battle_log, message, max_log=config.MAX_LOG_MESSAGES):
    battle_log.append(message)
    if len(battle_log) > max_log:
        battle_log.pop(0)