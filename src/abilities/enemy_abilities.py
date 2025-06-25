"""
This module defines the abilities available to enemies.

The list order of skills returned by helpers maps to skill slot indices 0..n,
even if the enemy AI does not use hotkeys, for consistency with the player's skill set.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from .base import Ability
from .player_abilities import AdrenalineRushAbility, ShieldBashAbility

if TYPE_CHECKING:
    from ..entities.base import Entity


__all__ = ["get_default_enemy_skills", "EnemyAttackAbility"]


class EnemyAttackAbility(Ability):  # pylint: disable=too-few-public-methods
    """The enemy's basic attack."""

    def __init__(self):
        super().__init__(name="Attack", base_cooldown=0)

    def execute(self, actor: Entity, target: Entity | None = None) -> dict:
        """
        Executes the attack, calculating damage.

        :param actor: The enemy entity.
        :param target: The player entity being attacked.
        :return: A dictionary with damage dealt.
        """
        # NOTE: Simplified compared to player attack. No miss/crit for now.
        damage = actor.attack
        target.take_damage(round(damage))  # type: ignore

        return {"damage": round(damage)}


def get_default_enemy_skills():
    """
    Return a list of Ability instances the enemy can use,
    slot-ordered for Q,W,E,R equivalence (unused for enemy but kept consistent).
    """
    return [
        ShieldBashAbility(),
        AdrenalineRushAbility(),
    ]
