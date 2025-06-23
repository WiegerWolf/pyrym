"""
explore.py
Manages the exploration state where the player can find items or trigger encounters.
"""
import random
from random import randint

from .. import config
from ..config import BASE_ENCOUNTER_CHANCE, ENCOUNTER_INCREMENT, ITEM_FIND_CHANCE
from ..core.state_machine import BaseState
from ..core.ui import UI
from ..items import HealingPotion, GoldPile
from ..utils import HealthBarSpec, handle_item_use, add_to_log


class ExploreState(BaseState):  # pylint: disable=too-many-instance-attributes
    """
    Manages the exploration phase of the game, where the player can find items
    or trigger encounters.
    """

    def __init__(self, player, meta, screen):
        """
        Initializes the exploration state.

        Args:
            player: The player character instance.
        """
        super().__init__()
        self.player = player
        self.meta = meta
        self.screen = screen
        self.log = []
        self.base_chance = BASE_ENCOUNTER_CHANCE
        self.step = ENCOUNTER_INCREMENT
        self.consecutive_turns = 0
        self.encounter_chance = self.base_chance
        self.item_menu_open = False

        add_to_log(self.log, "You are exploring the area.")

        # Retroactively convert any GoldPiles in inventory from old saves
        # to gold.
        for item in player.inventory[:]:
            if isinstance(item, GoldPile):
                item.use(player)
                player.remove_item(item)
                UI.notify(f"Converted {item.name} to {item.amount} gold.")

    def update(self, signals: dict) -> None:
        """
        Updates the exploration state based on player input.
        """
        if self.item_menu_open:
            self._handle_item_menu(signals)
        else:
            self._handle_player_actions(signals)

    def _handle_item_menu(self, signals: dict) -> None:
        """Handle input when the item menu is open."""
        if signals.get("use_item"):
            self.item_menu_open = False
        elif signals.get("number_keys"):
            key = signals["number_keys"][0]
            result = handle_item_use(self.player, key, lambda msg: add_to_log(self.log, msg))
            if result.get("success"):
                self.item_menu_open = False

    def _handle_player_actions(self, signals: dict) -> None:
        """Handle player actions when the item menu is closed."""
        if signals.get("explore"):
            self._explore_turn()
        elif signals.get("use_item"):
            if self.player.inventory:
                self.item_menu_open = True
            else:
                add_to_log(self.log, "Inventory is empty.")

    def _explore_turn(self) -> None:
        """
        Handles the logic for a single turn of exploration.
        Triggers encounters or item discoveries.
        """
        from ..entities import Enemy
        from .battle import BattleState  # Lazy import

        self.consecutive_turns += 1
        self.player.regenerate_stamina() # This is now handled by the ActionMixin

        # Check for encounter
        if random.random() < self.encounter_chance:
            self.encounter_chance = self.base_chance
            add_to_log(self.log, "An enemy approaches!")
            enemy = Enemy(encounter_index=self.meta.encounter_index)
            battle_state = BattleState(self.player, enemy, self.meta, self.screen)
            self.machine.change(battle_state)
            return

        # Check for finding an item
        if random.random() < ITEM_FIND_CHANCE:
            self._find_item()
        else:
            add_to_log(self.log, "You find nothing of interest.")

        self.encounter_chance += self.step
        # self.player.defend_ability.reset() # This is now handled by the ActionMixin

    def _find_item(self) -> None:
        """Generates and awards a random item to the player."""
        loot = random.choice([HealingPotion(), GoldPile(randint(5, 20))])
        if not loot.can_store:
            loot.use(self.player)
            add_to_log(self.log, f"You found {loot.amount} gold!")
        else:
            self.player.add_item(loot)
            add_to_log(self.log, f"You found a {loot.name}.")

    def render(self, screen):
        """
        Renders the exploration state.
        """
        screen.fill(config.BG_COLOR)

        inventory_pos = (config.SCREEN_WIDTH - 150, config.SCREEN_HEIGHT - 110)
        UI.render_inventory(screen, self.player.inventory, pos=inventory_pos)

        # Display player health
        player_health_spec = HealthBarSpec(
            *config.EXPLORE_PLAYER_HEALTH_POS,
            current=self.player.health,
            max_val=self.player.max_health,
            color=config.PLAYER_HEALTH_COLOR,
            label="Player"
        )
        UI.draw_health_bar(screen, player_health_spec)

        # Gold display
        UI.display_text(
            screen,
            f"Gold: {self.player.gold}",
            config.EXPLORE_GOLD_POS,
            font_size=config.LARGE_FONT_SIZE,
            color=config.TEXT_COLOR
        )

        # Display instructions
        instructions = ["(E)xplore"]
        if self.player.inventory:
            instructions.append("(I)tem")
        UI.display_text(
            screen, ", ".join(instructions),
            config.EXPLORE_INSTRUCTIONS_POS,
            font_size=config.MEDIUM_FONT_SIZE,
            color=config.UI_ACCENT_COLOR
        )

        # Display encounter chance
        UI.display_text(
            screen,
            f"Encounter Chance: {self.encounter_chance:.2f}",
            config.EXPLORE_ENCOUNTER_CHANCE_POS,
            font_size=config.MEDIUM_FONT_SIZE
        )

        if self.item_menu_open:
            UI.render_item_menu(screen, self.player)

        # Display log messages
        UI.render_explore_log(screen, self.log)
