from __future__ import annotations
import random
from typing import TYPE_CHECKING
from .base import Ability
import config

if TYPE_CHECKING:
    from entities import Entity

class PlayerAttackAbility(Ability):
    """The player's basic attack."""

    def __init__(self):
        super().__init__(name="Attack")

    def execute(self, actor: Entity, target: Entity) -> dict:
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
        base_damage = actor.attack
        
        damage_multiplier = random.uniform(*config.PLAYER_DMG_VARIATION)
        damage = base_damage * damage_multiplier
        
        if crit:
            damage *= config.PLAYER_CRIT_MULTIPLIER

        target.take_damage(round(damage))
        
        return {"damage": round(damage), "crit": crit, "miss": False}

class PlayerDefendAbility(Ability):
    """The player's defending ability."""

    def __init__(self):
        super().__init__(name="Defend")

    def execute(self, actor: Entity, target: Entity | None = None) -> dict:
        """
        Sets the actor's state to defending.

        :param actor: The player entity.
        :return: A dictionary indicating success.
        """
        actor.is_defending = True
        return {"success": True}