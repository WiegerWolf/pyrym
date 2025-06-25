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
    from ..entities.player import Player


class Item(ABC):
    """Abstract base class for items."""

    can_store: bool = True

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


class HealingPotion(Item):
    """An item that restores HP."""

    def __init__(self):
        super().__init__(
            name="Healing Potion",
            cost=config.HEALING_POTION_COST,
            description=f"Heals for {config.HEALING_POTION_HEAL_AMOUNT} HP."
        )

    def __repr__(self) -> str:
        return f"{self.name} (Cost: {self.cost})"

    def use(self, entity: Entity) -> dict:
        """Heal the entity."""
        entity.heal(config.HEALING_POTION_HEAL_AMOUNT)
        msg = f"Used {self.name}, healing {config.HEALING_POTION_HEAL_AMOUNT} HP."
        return {"message": msg, "value": config.HEALING_POTION_HEAL_AMOUNT}


class StaminaPotion(Item):
    """A potion that restores stamina."""

    def __init__(self):
        super().__init__(
            name="Stamina Potion",
            cost=config.STAMINA_POTION_COST,
            description=f"Gains {config.STAMINA_POTION_STAMINA_GAIN} stamina."
        )

    def __repr__(self) -> str:
        return f"{self.name} (Cost: {self.cost})"

    def use(self, entity: Entity) -> dict:
        """Add stamina to the entity."""
        if hasattr(entity, 'gain_stamina'):
            entity.gain_stamina(config.STAMINA_POTION_STAMINA_GAIN)
            msg = f"Used {self.name}, gaining {config.STAMINA_POTION_STAMINA_GAIN} stamina."
            print(msg)
            return {"message": msg, "value": config.STAMINA_POTION_STAMINA_GAIN}
        return {"message": f"{entity.name} cannot gain stamina.", "value": 0}

class GoldPile(Item):
    """
    Represents a pile of gold coins.
    On pickup, it directly adds to the player's gold instead of being an inventory item.
    """

    can_store: bool = False
    amount: int = 10

    def __init__(self, amount: int = 10):
        self.amount = amount
        super().__init__(
            name="Gold Pile",
            cost=0,  # Gold piles aren't bought, they are found.
            description=f"A pouch containing {self.amount} gold coins."
        )

    def __repr__(self) -> str:
        return f"Gold Pile ({self.amount})"

    def use(self, entity: "Player") -> dict:
        """Adds the gold amount to the game state."""
        entity.gain_gold(self.amount)
        msg = f"Added {self.amount} gold."
        return {"message": msg, "value": self.amount}


class Antidote(Item):
    """An item that cures negative status effects."""

    def __init__(self):
        super().__init__(
            name="Antidote",
            cost=config.ANTIDOTE_COST,
            description="Cures poison and other ailments."
        )

    def use(self, entity: Entity) -> dict:
        """Cures all negative statuses."""
        cleared_count = entity.clear_negative_statuses()
        if cleared_count > 0:
            msg = f"Used {self.name}, curing all negative effects."
            return {"message": msg, "value": cleared_count}
        
        msg = f"Used {self.name}, but there was nothing to cure."
        return {"message": msg, "value": 0}
