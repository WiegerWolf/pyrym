"""
base.py
Base class for all entities in the game.
"""
from __future__ import annotations
import abc
from math import ceil
from src import config

class Entity(abc.ABC):
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
