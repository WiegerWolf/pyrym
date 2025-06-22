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
        """Sets the block_active flag and gains stamina."""
        self.block_active = True
        self.gain_stamina(1)

    def gain_stamina(self, amount: int):
        """Gains stamina, up to the max."""
        self.stamina = min(self.max_stamina, self.stamina + amount)

    def spend_stamina(self, amount: int):
        """Spends stamina."""
        self.stamina = max(0, self.stamina - amount)

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

    def reset(self):
        """Resets player stats to their base values for a new battle."""
        self.health = self.max_health
        self.stamina = 1
        self.block_active = False

    @property
    def is_defending(self):
        """Returns True if the player is defending."""
        return self.block_active
