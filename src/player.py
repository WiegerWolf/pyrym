import random


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
        if random.random() < 0.1:
            miss = True
            damage = 0
        elif random.random() < 0.15:
            crit = True
            damage = int(self.attack_power * 1.5)
        else:
            damage = int(self.attack_power * random.uniform(0.7, 1.3))
        enemy.take_damage(damage)
        return damage, crit, miss

    def take_damage(self, damage):
        if self.is_defending:
            damage = int(damage * 0.5)  # Reduce damage by 50% when defending
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