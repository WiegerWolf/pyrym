"""
mixins.py
Provides mixin classes for entities.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import Entity


class ActionMixin:
    """Mixin for common entity actions like attacking and defending."""

    def attack_action(self, target: Entity) -> dict:
        """Wrapper for the attack ability."""
        if hasattr(self, 'stamina') and self.stamina < 1:
            return {"damage": 0, "crit": False, "miss": False, "no_stamina": True}

        if not hasattr(self, 'attack_ability'):
            raise NotImplementedError("Component must have an `attack_ability`.")

        if hasattr(self, 'spend_stamina'):
            self.spend_stamina(1)

        result = self.attack_ability.execute(self, target)
        return result

    def defend(self):
        """Sets the block_active flag and gains stamina."""
        self.block_active = True
        self.gain_stamina(1)

    def gain_stamina(self, amount: int):
        """Gains stamina, up to the max."""
        self.stamina = min(self.max_stamina, self.stamina + amount)

    def spend_stamina(self, amount: int):
        """Spends stamina."""
        self.stamina = max(0, self.stamina - amount)
