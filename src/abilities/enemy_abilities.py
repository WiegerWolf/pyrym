"""
enemy_abilities.py
Defines the enemy's abilities.
"""
from __future__ import annotations

import random
from typing import TYPE_CHECKING

from src import config

from .base import Ability

if TYPE_CHECKING:
    from ..entities.base import Entity

class EnemyAttackAbility(Ability):  # pylint: disable=too-few-public-methods
    """The enemy's basic attack."""

    def __init__(self):
        super().__init__(name="Attack")

    def execute(self, actor: Entity, target: Entity | None = None) -> dict:
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

        if target.block_active:
            damage *= (1 - config.DEFEND_BLOCK)
            target.block_active = False

        target.take_damage(round(damage))

        return {"damage": round(damage), "crit": crit, "miss": False}
