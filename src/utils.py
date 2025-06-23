"""
utils.py
Utility helpers used throughout the game package.
"""
from dataclasses import dataclass
from typing import Tuple

import pygame
from src import config

@dataclass
class EncounterMeta:
    """A dataclass to hold metadata for a battle encounter."""
    score: int
    wave: int
    fled: bool = False

    def reset(self):
        """Resets transient flags for a new encounter."""
        self.fled = False

@dataclass
class HealthBarSpec:
    """A dataclass to hold the specifications for rendering a health bar."""
    x: int
    y: int
    current: int
    max_val: int
    color: Tuple[int, int, int]
    label: str

def load_image(file_path):
    """Load an image from the specified file path."""
    image = pygame.image.load(file_path)
    return image

def manage_game_settings(_settings):
    """Manage game settings such as volume, difficulty, etc."""
    # Placeholder for managing game settings


def add_to_log(battle_log, message, max_log=config.MAX_LOG_MESSAGES):
    """Add a message to the battle log, ensuring it doesn't exceed the max size."""
    battle_log.append(message)
    if len(battle_log) > max_log:
        battle_log.pop(0)
