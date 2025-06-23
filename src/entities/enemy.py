"""
enemy.py
Defines the enemy characters.
"""
from .. import config
from .base import Entity
from .mixins import ActionMixin
from ..abilities.enemy_abilities import EnemyAttackAbility

class Enemy(Entity, ActionMixin):
    """The enemy entity."""

    def __init__(self, encounter_index=1):
        base_health = config.ENEMY_BASE_HEALTH + (encounter_index - 1) * config.ENEMY_HEALTH_SCALING
        self.health = base_health
        base_attack = config.ENEMY_BASE_ATTACK + (encounter_index - 1) * config.ENEMY_ATTACK_SCALING
        super().__init__(name=f"Enemy lvl {encounter_index}", health=self.health, attack=base_attack)
        self.encounter_index = encounter_index

        # Abilities
        self.attack_ability = EnemyAttackAbility()

    def reset(self):
        """Resets the enemy's stats for a new encounter."""
        self.health = self.max_health
        self.stamina = 1
        self.block_active = False
