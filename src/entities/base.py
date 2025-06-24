"""
base.py
Base class for all entities in the game.
"""
from __future__ import annotations
import abc
from math import ceil
from typing import List, Type
from src import config
from .status import Status


# pylint: disable=cyclic-import
class Entity(abc.ABC):  # pylint: disable=too-many-instance-attributes
    """
    Base class for any entity in the game, like Player or Enemy.
    """
    def __init__(self, name: str, health: int, attack: int):
        """Initialize a base entity."""
        self.name = name
        self.max_health = health
        self.health = health
        self.attack = attack
        self.max_stamina: int = config.MAX_STAMINA
        self.stamina: int = 1
        self.block_active: bool = False
        self.statuses: List[Status] = []
        self.stunned: bool = False

    def apply_status(self, status: Status) -> None:
        """Append a fresh Status and immediately call its on_apply hook."""
        self.statuses.append(status)
        status.on_apply(self)

    def tick_statuses(self, battle_state) -> None:
        """Tick each active Status at the start of the entity’s turn.
        Removes expired statuses."""
        expired: list[Status] = []
        for s in self.statuses:
            if s.tick(self, battle_state):
                expired.append(s)
        for s in expired:
            self.statuses.remove(s)

    def has_status(self, status_type: Type[Status]) -> bool:
        """Return True if an active status of given subclass exists."""
        return any(isinstance(s, status_type) for s in self.statuses)

    def take_damage(self, raw_damage: int):
        """
        Calculates final damage based on block and applies it.
        This can be overridden for more complex logic.
        """
        if self.block_active:
            final_damage = ceil(raw_damage * (1 - config.DEFEND_BLOCK))
            self.block_active = False  # Block is consumed
        else:
            final_damage = raw_damage

        self.health -= final_damage
        self.health = max(self.health, 0)


    def heal(self, amount: int):
        """Heal the entity for a given amount."""
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health

    def is_alive(self) -> bool:
        """Check if the entity is alive."""
        return self.health > 0
