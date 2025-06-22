"""
player.py
Defines the player character.
"""
from src import config
from .base import Entity
from ..abilities import PlayerAttackAbility, PlayerDefendAbility
from ..items import Item, HealingPotion


class Player(Entity):
    """The player entity."""

    def __init__(self):
        super().__init__(
            name="Player",
            health=config.PLAYER_BASE_HEALTH,
            attack=config.PLAYER_BASE_ATTACK,
        )
        self.gold = 0
        self.inventory: list[Item] = [HealingPotion(20) for _ in range(3)]

        # Abilities
        self.attack_ability = PlayerAttackAbility()
        self.defend_ability = PlayerDefendAbility()

    def attack_action(self, target: Entity) -> tuple[int, bool, bool]:
        """Wrapper for the attack ability."""
        result = self.attack_ability.execute(self, target)
        return result["damage"], result["crit"], result["miss"]

    def defend(self):
        """Wrapper for the defend ability."""
        self.defend_ability.execute(self)

    def add_item(self, item: Item):
        """Adds an item to the player's inventory."""
        self.inventory.append(item)

    def has_potion(self) -> bool:
        """Checks if the player has any healing potions."""
        return any(isinstance(item, HealingPotion) for item in self.inventory)

    def use_potion(self) -> int:
        """
        Uses a healing potion from the inventory and returns the amount healed.
        Returns 0 if no potion was used.
        """
        for item in self.inventory:
            if isinstance(item, HealingPotion):
                heal_amount = item.heal_amount
                item.apply(self)
                self.inventory.remove(item)
                return heal_amount
        return 0

    def take_damage(self, damage: int):
        """Reduces player health by the given damage amount."""
        self.health -= damage
        self.health = max(self.health, 0)

    def reset(self):
        """Resets player stats to their base values."""
        self.health = self.max_health
        self.is_defending = False
