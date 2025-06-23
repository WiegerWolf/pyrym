"""
utils.py
Utility helpers used throughout the game package.
"""
from dataclasses import dataclass
from typing import Tuple
from collections import OrderedDict

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


def group_inventory(inventory: list) -> list[tuple[any, int, int]]:
    """
    Groups items in the inventory by name, counting quantities and tracking the
    index of the first item of each a kind.

    Args:
        inventory: A list of item objects.

    Returns:
        A list of tuples, where each tuple contains (item, quantity, first_index).
    """
    if not inventory:
        return []

    # Use OrderedDict to preserve the order of items as they appear
    grouped = OrderedDict()
    for i, item in enumerate(inventory):
        if item.name not in grouped:
            grouped[item.name] = {'item': item, 'qty': 0, 'indices': []}
        grouped[item.name]['qty'] += 1
        grouped[item.name]['indices'].append(i)

    # Convert to the desired output format
    result = []
    for name, data in grouped.items():
        first_index = min(data['indices'])
        result.append((data['item'], data['qty'], first_index))

    return result


def handle_item_use(player, key, logger_callback) -> dict:
    """
    Handles the logic for using an item from the inventory based on a key press.
    This version handles a grouped inventory.

    Args:
        player: The player entity.
        key: The pygame key code that was pressed.
        logger_callback: A function to call with notifications (e.g., UI.notify).

    Returns:
        A dictionary with the result of the action.
    """
    selected_index = key - pygame.key.key_code("1")
    grouped_inventory = group_inventory(player.inventory)

    if 0 <= selected_index < len(grouped_inventory):
        # Get the actual index from the grouped list
        _, _, actual_index = grouped_inventory[selected_index]
        result = player.use_item(actual_index)
        if result:
            logger_callback(result["message"])
            return {"success": True, "used_item": True}
        return {"success": False, "used_item": False}

    logger_callback("Invalid item selection.")
    return {"success": False, "used_item": False}

def scaled_cost(base: int, level: int, growth: float) -> int:
    """Calculates the scaling cost for leveled upgrades."""
    return int(round(base * (growth ** level)))
