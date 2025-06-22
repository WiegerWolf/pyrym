from src import config
from src.entities.base import Entity
from src.abilities.enemy_abilities import EnemyAttackAbility

class Enemy(Entity):
    """The enemy entity."""

    def __init__(self, wave=1):
        base_health = config.ENEMY_BASE_HEALTH + (wave - 1) * config.ENEMY_HEALTH_SCALING
        base_attack = config.ENEMY_BASE_ATTACK + (wave - 1) * config.ENEMY_ATTACK_SCALING
        super().__init__(name=f"Enemy Wave {wave}", health=base_health, attack=base_attack)
        self.wave = wave

        # Abilities
        self.attack_ability = EnemyAttackAbility()

    def attack_action(self, target: Entity) -> tuple[int, bool, bool]:
        """Wrapper for the attack ability."""
        result = self.attack_ability.execute(self, target)
        return result["damage"], result["crit"], result["miss"]

    def take_damage(self, damage: int):
        """Reduces enemy health by the given damage amount."""
        self.health -= damage
        if self.health < 0:
            self.health = 0