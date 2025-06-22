"""
items.py
Defines all items in the game.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..entities.player import Player


class Item(ABC):
    """Abstract base class for items."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

    def __repr__(self) -> str:
        return self.name

    @abstractmethod
    def apply(self, player: Player) -> None:
        """Apply the item's effect to the player."""
        raise NotImplementedError


class HealingPotion(Item):
    """A potion that heals the player."""

    def __init__(self, amount: int):
        super().__init__(name="Healing Potion", description=f"Heals for {amount} HP.")
        self.heal_amount = amount

    def apply(self, player: Player) -> None:
        """Heal the player."""
        # Assuming player has a 'heal' method or similar attribute.
        # This might need to be adapted to the actual Player class implementation.
        if hasattr(player, 'health') and hasattr(player, 'max_health'):
            player.health = min(player.max_health, player.health + self.heal_amount)


class GoldPile(Item):
    """A pile of gold."""

    def __init__(self, amount: int):
        super().__init__(name="Gold Pile", description=f"{amount} gold pieces.")
        self.amount = amount

    def apply(self, player: Player) -> None:
        """Add gold to the player's inventory."""
        if not hasattr(player, 'gold'):
            player.gold = 0
        player.gold += self.amount
