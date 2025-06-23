"""
mixins.py
Provides mixin classes for entities.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from .base import Entity


class ActionMixin:
    """Mixin for common entity actions like attacking and defending."""

    def attack_action(self, target: Entity) -> Tuple[int, bool, bool]:
        """Wrapper for the attack ability."""
        if not hasattr(self, 'attack_ability'):
            raise NotImplementedError("Component must have an `attack_ability`.")
        result = self.attack_ability.execute(self, target)
        return result["damage"], result["crit"], result["miss"]

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
