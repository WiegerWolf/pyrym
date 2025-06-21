import random
import config


class Player:
    def __init__(self, name, health, attack_power):
        self.name = name
        self.health = health
        self.attack_power = attack_power
        self.is_defending = False

    def attack(self, enemy):
        # Randomize damage: 70%-130% of attack_power
        crit = False
        miss = False
        if random.random() < config.PLAYER_MISS_CHANCE:
            miss = True
            damage = 0
        elif random.random() < config.PLAYER_CRIT_CHANCE:
            crit = True
            damage = int(self.attack_power * config.PLAYER_CRIT_MULTIPLIER)
        else:
            damage = int(self.attack_power * random.uniform(*config.PLAYER_DMG_VARIATION))
        enemy.take_damage(damage)
        return damage, crit, miss

    def take_damage(self, damage):
        if self.is_defending:
            damage = int(damage * config.DEFEND_DAMAGE_REDUCTION)  # Reduce damage by 50% when defending
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def is_alive(self):
        return self.health > 0

    def heal(self, max_health, amount):
        heal_amount = min(amount, max_health - self.health)
        self.health += heal_amount
        return heal_amount

    def defend(self):
        self.is_defending = True

    def reset_defend(self):
        self.is_defending = False