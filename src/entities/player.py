"""
player.py
Defines the player character.
"""
from src import config
from .base import Entity
from ..abilities import PlayerAttackAbility, PlayerDefendAbility
from ..items.items import Item


class Player(Entity):
    """The player entity."""

    def __init__(self):
        super().__init__(
            name="Player",
            health=config.PLAYER_BASE_HEALTH,
            attack=config.PLAYER_BASE_ATTACK,
        )
        self.inventory: list[Item] = []

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
        print(f"Added {item.name} to inventory.")

    def remove_item(self, item: Item):
        """Removes an item from the player's inventory."""
        if item in self.inventory:
            self.inventory.remove(item)
            print(f"Removed {item.name} from inventory.")

    def use_item(self, index: int) -> dict | None:
        """
        Uses an item from the inventory by its index.
        Returns the result from the item's use() method.
        """
        if 0 <= index < len(self.inventory):
            item = self.inventory[index]
            result = item.use(self)
            self.remove_item(item)
            return result
        return None

    def new_game_reset(self):
        """Resets the player for a new game."""
        self.health = self.max_health
        self.stamina = 1
        self.block_active = False
        self.inventory = []

    def reset(self):
        """Resets player stats to their base values for a new battle."""
        self.health = self.max_health
        self.stamina = 1
        self.block_active = False

    @property
    def is_defending(self):
        """Returns True if the player is defending."""
        return self.block_active
