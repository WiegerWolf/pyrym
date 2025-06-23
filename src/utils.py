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
    encounter_index: int
    fled: bool = False
    turns: int = 0
    battles_won: int = 0

    def reset(self):
        """Resets transient flags for a new encounter."""
        self.fled = False
        self.turns = 0

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


def handle_item_use(player, key, logger_callback) -> dict:
    """
    Handles the logic for using an item from the inventory based on a key press.

    Args:
        player: The player entity.
        key: The pygame key code that was pressed.
        logger_callback: A function to call with notifications (e.g., UI.notify).

    Returns:
        A dictionary with the result of the action.
    """
    index = key - pygame.key.key_code("1")
    if 0 <= index < len(player.inventory):
        result = player.use_item(index)
        if result:
            logger_callback(result["message"])
            return {"success": True, "used_item": True}
        return {"success": False, "used_item": False}

    logger_callback("Invalid item selection.")
    return {"success": False, "used_item": False}

def scaled_cost(base: int, level: int, growth: float) -> int:
    """Calculates the scaling cost for leveled upgrades."""
    return int(round(base * (growth ** level)))
