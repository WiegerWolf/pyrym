"""
player_abilities.py
Defines the player's abilities.
"""
from __future__ import annotations

import random
from typing import TYPE_CHECKING

from src import config

from .base import Ability

if TYPE_CHECKING:
    from ..entities.base import Entity


__all__ = [
    "PlayerAttackAbility",
    "PlayerDefendAbility",
    "ShieldBashAbility",
    "AdrenalineRushAbility",
]


class PlayerAttackAbility(Ability):  # pylint: disable=too-few-public-methods
    """The player's basic attack."""

    def __init__(self):
        super().__init__(name="Attack", base_cooldown=0)

    def execute(self, actor: Entity, target: Entity | None = None) -> dict:
        """
        Executes the attack, calculating damage, crit, and miss chances.

        :param actor: The player entity.
        :param target: The enemy entity being attacked.
        :return: A dictionary with damage, crit status, and miss status.
        """
        miss = random.random() < config.PLAYER_MISS_CHANCE
        if miss:
            return {"damage": 0, "crit": False, "miss": True}

        crit = random.random() < config.PLAYER_CRIT_CHANCE
        base_damage = (actor.attack + actor.power_strike_bonus) * actor.damage_mult

        damage_multiplier = random.uniform(*config.PLAYER_DMG_VARIATION)
        damage = base_damage * damage_multiplier

        if crit:
            damage *= config.PLAYER_CRIT_MULTIPLIER

        target.take_damage(round(damage))

        return {"damage": round(damage), "crit": crit, "miss": False}

class PlayerDefendAbility(Ability):  # pylint: disable=too-few-public-methods
    """The player's defending ability."""

    def __init__(self):
        super().__init__(name="Defend", base_cooldown=0)

    def execute(self, actor: Entity, target: Entity | None = None) -> dict:
        """
        Sets the actor's state to defending.

        :param actor: The player entity.
        :return: A dictionary indicating success.
        """
        actor.is_defending = True
        return {"success": True}


class ShieldBashAbility(Ability):
    """
    Shield Bash – 75 % normal damage + apply StunStatus(1) to the target.
    3-turn cool-down.
    """
    def __init__(self):
        super().__init__(
            name="Shield Bash",
            stamina_cost=2,
            base_cooldown=3
        )

    def execute(self, actor: Entity, target: Entity | None = None, battle_context=None) -> dict:
        self.on_use(actor)
        # damage: 0.75 × actor.attack stat (reuse existing damage helper if any)
        dmg = int(actor.attack * 0.75)
        target.take_damage(dmg)

        # Apply stun if StunStatus class exists; otherwise TODO comment
        try:
            from src.entities.status import StunStatus
            target.apply_status(StunStatus(duration=1))
            return {"damage": dmg, "stun": True}
        except ImportError:
            return {"damage": dmg, "stun": False}


class AdrenalineRushAbility(Ability):
    """
    Gain +2 stamina immediately. 4-turn cool-down.
    """
    def __init__(self):
        super().__init__(name="Adrenaline Rush", stamina_cost=0, base_cooldown=4)

    def execute(self, actor: Entity, target: Entity | None = None, battle_context=None) -> dict:
        self.on_use(actor)
        actor.gain_stamina(2)
        return {"stamina_gain": 2}
