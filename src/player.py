import config
from entities import Entity
from abilities import PlayerAttackAbility, PlayerHealAbility, PlayerDefendAbility
from items import Item, HealingPotion


class Player(Entity):
    """The player entity."""

    def __init__(self):
        super().__init__(
            name="Player",
            health=config.PLAYER_BASE_HEALTH,
            attack=config.PLAYER_BASE_ATTACK,
        )
        self.potions = 3
        self.gold = 0
        self.inventory: list[Item] = []

        # Abilities
        self.attack_ability = PlayerAttackAbility()
        self.heal_ability = PlayerHealAbility()
        self.defend_ability = PlayerDefendAbility()

    def attack_action(self, target: Entity) -> tuple[int, bool, bool]:
        """Wrapper for the attack ability."""
        result = self.attack_ability.execute(self, target)
        return result["damage"], result["crit"], result["miss"]

    def heal_action(self) -> int:
        """Wrapper for the heal ability."""
        result = self.heal_ability.execute(self)
        return result["heal_amount"]

    def defend(self):
        """Wrapper for the defend ability."""
        self.defend_ability.execute(self)

    def add_item(self, item: Item):
        """Adds an item to the player's inventory."""
        self.inventory.append(item)

    def use_potion(self) -> bool:
        """Uses a healing potion from the inventory."""
        for item in self.inventory:
            if isinstance(item, HealingPotion):
                item.apply(self)
                self.inventory.remove(item)
                return True
        return False

    def take_damage(self, damage: int):
        """Reduces player health by the given damage amount."""
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def reset(self):
        """Resets player stats to their base values."""
        self.health = self.max_health
        self.is_defending = False
        self.potions = 3