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

    def __init__(self, wave=1):
        base_health = config.ENEMY_BASE_HEALTH + (wave - 1) * config.ENEMY_HEALTH_SCALING
        self.health = base_health
        base_attack = config.ENEMY_BASE_ATTACK + (wave - 1) * config.ENEMY_ATTACK_SCALING
        super().__init__(name=f"Enemy Wave {wave}", health=self.health, attack=base_attack)
        self.wave = wave

        # Abilities
        self.attack_ability = EnemyAttackAbility()

    def reset(self):
        """Resets the enemy's stats for a new encounter."""
        self.health = self.max_health
        self.stamina = 1
        self.block_active = False
