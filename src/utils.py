"""
utils.py
Utility helpers used throughout the game package.
"""
from dataclasses import dataclass
from typing import Tuple, Type, TYPE_CHECKING
from collections import OrderedDict

import pygame
from src import config
from .entities.status import Status

if TYPE_CHECKING:
    from .entities.base import Entity
    from .core.battle_log import BattleLog


@dataclass
class EncounterMeta:
    """A dataclass to hold metadata for a battle encounter."""
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
    for _, data in grouped.items():
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
def give_status(
    target: "Entity",
    status_cls: Type[Status],
    duration: int,
    log_callback: "BattleLog" = None
):
    """
    Apply or refresh a status effect on the target Entity.

    Args:
        target (Entity): The entity receiving the status.
        status_cls (Type[Status]): Concrete Status subclass to apply.
        duration (int): Number of turns the status should last.
        log_callback (Callable[[str], None] | None): Optional function to append
            messages to the battle log.
    """
    # Check if status already active -> refresh duration
    for s in target.statuses:
        if isinstance(s, status_cls):
            s.duration = max(s.duration, duration)
            if log_callback:
                add_to_log(
                    log_callback,
                    f"{target.name} already has {s.name}. "
                    f"Duration refreshed to {s.duration}."
                )
            return

    # Otherwise, apply a fresh instance
    new_status = status_cls(duration)
    target.apply_status(new_status)
    if log_callback:
        add_to_log(
            log_callback,
            f"{target.name} is afflicted by {new_status.name} ({duration})."
        )


def inflict_damage(player: "Entity", damage: int, log_callback: "BattleLog" = None):
    """Inflicts damage on the player and logs it."""
    player.take_damage(damage)
    if log_callback:
        add_to_log(log_callback, f"You took {damage} damage!")


def scaled_cost(base: int, level: int, growth: float) -> int:
    """Calculates the scaling cost for leveled upgrades."""
    return int(round(base * (growth ** level)))
