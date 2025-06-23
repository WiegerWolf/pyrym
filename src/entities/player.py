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
    xp: int = 0
    gold: int = 0


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

    def __repr__(self):
        return (f"Player(HP: {self.health}/{self.max_health}, "
                f"XP: {self.xp}, Gold: {self.gold})")

    @property
    def xp(self) -> int:
        """Returns the player's experience points."""
        return self.state.xp

    @property
    def gold(self) -> int:
        """Returns the player's gold."""
        return self.state.gold

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

    def remove_item(self, item: Item):
        """Removes an item from the player's inventory."""
        if item in self.state.inventory:
            self.state.inventory.remove(item)

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

    def gain_xp(self, amount: int):
        """Adds experience points to the player."""
        if amount > 0:
            self.state.xp = min(self.state.xp + amount, 999_999)

    def spend_xp(self, amount: int) -> bool:
        """Spends experience points if available."""
        if self.state.xp >= amount:
            self.state.xp -= amount
            return True
        return False

    def gain_gold(self, amount: int):
        """Adds gold to the player."""
        if amount > 0:
            self.state.gold += amount

    def spend_gold(self, amount: int) -> bool:
        """Spends gold if available."""
        if self.state.gold >= amount:
            self.state.gold -= amount
            return True
        return False

    def regenerate_stamina(self, amount: int = 1):
        """Called each turn to regenerate stamina."""
        # This method is now found in the ActionMixin and is no longer needed here.
        pass

    def reset(self):
        """Resets the player for a new game."""
        self.max_health = config.PLAYER_BASE_HEALTH
        self.health = self.max_health
        self.stamina = 1
        self.block_active = False
        self.state = PlayerState()

    def battle_reset(self):
        """Resets player stats for a new battle, preserving health."""
        # Cap stamina at max, but don't reset it.
        self.stamina = min(self.stamina, config.MAX_STAMINA)
        self.block_active = False

    def gain_stamina(self, amount: int):
        """Adds stamina to the player."""
        if amount > 0:
            self.stamina = min(self.stamina + amount, config.MAX_STAMINA)

    @property
    def is_defending(self):
        """Returns True if the player is defending."""
        return self.block_active


if __name__ == '__main__':
    # Minimal unit-style test
    player = Player()
    player.gain_xp(30)
    assert player.xp == 30, f"Expected 30 XP, got {player.xp}"

    assert player.spend_xp(10) is True, "spend_xp(10) should return True"
    assert player.xp == 20, f"Expected 20 XP after spending, got {player.xp}"

    assert player.spend_xp(25) is False, "spend_xp(25) should return False"
    assert player.xp == 20, f"XP should not change after failed spend, got {player.xp}"

    player.gain_gold(100)
    assert player.gold == 100, f"Expected 100 gold, got {player.gold}"

    print("Player XP and Gold tests passed!")
