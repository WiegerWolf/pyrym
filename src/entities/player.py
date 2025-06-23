"""
player.py
Defines the player character.
"""
from dataclasses import dataclass, field
from src import config
from .base import Entity
from .mixins import ActionMixin
from ..abilities import PlayerAttackAbility, PlayerDefendAbility
from ..items.items import Item


@dataclass
class PlayerState:
    """A container for player-specific state."""
    inventory: list[Item] = field(default_factory=list)
    power_strike_bonus: int = 0


class Player(Entity, ActionMixin):
    """The player entity."""

    def __init__(self):
        super().__init__(
            name="Player",
            health=config.PLAYER_BASE_HEALTH,
            attack=config.PLAYER_BASE_ATTACK,
        )
        self.state = PlayerState()

        # Abilities
        self.attack_ability = PlayerAttackAbility()
        self.defend_ability = PlayerDefendAbility()

    @property
    def inventory(self):
        """Backwards compatibility for inventory access."""
        return self.state.inventory

    @property
    def power_strike_bonus(self) -> int:
        """Forward the power_strike_bonus stored in the nested PlayerState."""
        return self.state.power_strike_bonus

    def add_item(self, item: Item):
        """Adds an item to the player's inventory."""
        self.state.inventory.append(item)
        print(f"Added {item.name} to inventory.")

    def remove_item(self, item: Item):
        """Removes an item from the player's inventory."""
        if item in self.state.inventory:
            self.state.inventory.remove(item)
            print(f"Removed {item.name} from inventory.")

    def use_item(self, index: int) -> dict | None:
        """
        Uses an item from the inventory by its index.
        Returns the result from the item's use() method.
        """
        if 0 <= index < len(self.state.inventory):
            item = self.state.inventory[index]
            result = item.use(self)
            self.remove_item(item)
            return result
        return None

    def new_game_reset(self):
        """Resets the player for a new game."""
        self.max_health = config.PLAYER_BASE_HEALTH
        self.health = self.max_health
        self.stamina = 1
        self.block_active = False
        self.state = PlayerState()

    def reset(self):
        """Resets player stats to their base values for a new battle."""
        self.health = self.max_health
        self.stamina = 1
        self.block_active = False

    @property
    def is_defending(self):
        """Returns True if the player is defending."""
        return self.block_active
