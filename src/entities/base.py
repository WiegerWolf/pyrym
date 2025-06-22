from __future__ import annotations
import abc

class Entity(abc.ABC):
    """
    Base class for any entity in the game, like Player or Enemy.
    """
    def __init__(self, name: str, health: int, attack: int):
        self.name = name
        self.max_health = health
        self.health = health
        self.attack = attack
        self.is_defending = False

    @abc.abstractmethod
    def take_damage(self, damage: int):
        raise NotImplementedError

    def heal(self, amount: int):
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health

    def is_alive(self) -> bool:
        return self.health > 0
