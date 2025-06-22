from __future__ import annotations
import random
from typing import TYPE_CHECKING
from .base import Ability
import config

if TYPE_CHECKING:
    from entities import Entity

class EnemyAttackAbility(Ability):
    """The enemy's basic attack."""

    def __init__(self):
        super().__init__(name="Attack")

    def execute(self, actor: Entity, target: Entity) -> dict:
        """
        Executes the attack, calculating damage, crit, and miss chances.

        :param actor: The enemy entity.
        :param target: The player entity being attacked.
        :return: A dictionary with damage, crit status, and miss status.
        """
        miss = random.random() < config.ENEMY_MISS_CHANCE
        if miss:
            return {"damage": 0, "crit": False, "miss": True}

        crit = random.random() < config.ENEMY_CRIT_CHANCE
        base_damage = actor.attack
        
        damage_multiplier = random.uniform(*config.ENEMY_DMG_VARIATION)
        damage = base_damage * damage_multiplier
        
        if crit:
            damage *= config.ENEMY_CRIT_MULTIPLIER

        if target.is_defending:
            damage *= (1 - config.DEFEND_DAMAGE_REDUCTION)
            target.is_defending = False

        target.take_damage(round(damage))
        
        return {"damage": round(damage), "crit": crit, "miss": False}