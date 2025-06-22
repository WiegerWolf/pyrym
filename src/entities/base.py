"""
base.py
Base class for all entities in the game.
"""
from __future__ import annotations
import abc

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
        self.is_defending = False

    @abc.abstractmethod
    def take_damage(self, damage: int):
        """Take damage from an attack."""
        raise NotImplementedError

    def heal(self, amount: int):
        """Heal the entity for a given amount."""
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health

    def is_alive(self) -> bool:
        """Check if the entity is alive."""
        return self.health > 0
