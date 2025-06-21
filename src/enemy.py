import random
import config


class Enemy:
    def __init__(self, name, health, attack_power):
        self.name = name
        self.health = health
        self.attack_power = attack_power
        self.is_defending = False

    def attack(self, player):
        # Randomize damage: 70%-130% of attack_power
        crit = False
        miss = False
        if random.random() < config.ENEMY_MISS_CHANCE:
            miss = True
            damage = 0
        elif random.random() < config.ENEMY_CRIT_CHANCE:
            crit = True
            damage = int(self.attack_power * config.ENEMY_CRIT_MULTIPLIER)
        else:
            damage = int(self.attack_power * random.uniform(*config.ENEMY_DMG_VARIATION))
        player.take_damage(damage)
        return damage, crit, miss

    def take_damage(self, damage):
        if self.is_defending:
            damage = int(damage * config.DEFEND_DAMAGE_REDUCTION)  # Reduce damage by 50% if defending
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def defend(self):
        self.is_defending = True

    def reset_defend(self):
        self.is_defending = False

    def is_alive(self):
        return self.health > 0

    def __str__(self):
        return f"{self.name} (Health: {self.health}, Attack Power: {self.attack_power})"