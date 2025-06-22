"""
items.py
Defines all items in the game.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from src import config

if TYPE_CHECKING:
    from ..entities.base import Entity


class Item(ABC):
    """Abstract base class for items."""

    def __init__(self, name: str, cost: int, description: str = ""):
        self.name = name
        self.cost = cost
        self.description = description

    def __repr__(self) -> str:
        return f"{self.name} (Cost: {self.cost})"

    @abstractmethod
    def use(self, entity: Entity) -> dict:
        """
        Apply the item's effect to the entity.
        Returns a dictionary with details about the action, e.g.,
        {"message": "Healed for 30 HP", "value": 30}
        """
        raise NotImplementedError


class HealingSalve(Item):
    """An item that restores HP."""

    def __init__(self):
        super().__init__(
            name="Healing Salve",
            cost=config.HEALING_SALVE_COST,
            description=f"Heals for {config.HEALING_SALVE_HEAL_AMOUNT} HP."
        )

    def use(self, entity: Entity) -> dict:
        """Heal the entity."""
        entity.heal(config.HEALING_SALVE_HEAL_AMOUNT)
        msg = f"Used {self.name}, healing {config.HEALING_SALVE_HEAL_AMOUNT} HP."
        print(msg)
        return {"message": msg, "value": config.HEALING_SALVE_HEAL_AMOUNT}


class StaminaPotion(Item):
    """A potion that restores stamina."""

    def __init__(self):
        super().__init__(
            name="Stamina Potion",
            cost=config.STAMINA_POTION_COST,
            description=f"Gains {config.STAMINA_POTION_STAMINA_GAIN} stamina."
        )

    def use(self, entity: Entity) -> dict:
        """Add stamina to the entity."""
        if hasattr(entity, 'gain_stamina'):
            entity.gain_stamina(config.STAMINA_POTION_STAMINA_GAIN)
            msg = f"Used {self.name}, gaining {config.STAMINA_POTION_STAMINA_GAIN} stamina."
            print(msg)
            return {"message": msg, "value": config.STAMINA_POTION_STAMINA_GAIN}
        return {"message": f"{entity.name} cannot gain stamina.", "value": 0}
