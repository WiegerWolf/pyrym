"""
explore.py
Manages the exploration state where the player can find items or trigger encounters.
"""
import random
from random import randint

from .. import config
from ..config import BASE_ENCOUNTER_CHANCE, ENCOUNTER_INCREMENT, ITEM_FIND_CHANCE
from ..core.game_state import StateManager
from ..core.ui import UI
from ..items import HealingPotion, GoldPile
from ..utils import HealthBarSpec, handle_item_use, add_to_log


class ExploreState:
    """
    Manages the exploration phase of the game, where the player can find items
    or trigger encounters.
    """

    def __init__(self, screen, player):
        """
        Initializes the exploration state.

        Args:
            screen: The screen surface to draw on.
            player: The player character instance.
        """
        self.screen = screen
        self.player = player
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

    def update(self, signals):
        """
        Updates the exploration state based on player input.
        """
        if self.item_menu_open:
            return self._handle_item_menu(signals)
        return self._handle_player_actions(signals)

    def _handle_item_menu(self, signals):
        """Handle input when the item menu is open."""
        if signals.get("use_item"):
            self.item_menu_open = False
        elif signals.get("number_keys"):
            key = signals["number_keys"][0]
            result = handle_item_use(self.player, key, UI.notify)
            if result.get("success"):
                self.item_menu_open = False
                return {"used_item": True}
        return None

    def _handle_player_actions(self, signals):
        """Handle player actions when the item menu is closed."""
        if signals.get("search"):  # Continue exploring
            return self._explore_turn()
        if signals.get("use_item"):
            if self.player.inventory:
                self.item_menu_open = True
            else:
                UI.notify("Inventory is empty.")
        return None

    def _explore_turn(self):
        """
        Handles the logic for a single turn of exploration.

        Returns:
            dict: A dictionary indicating if an encounter occurred.
        """
        if random.random() < self.encounter_chance:
            self.encounter_chance = self.base_chance  # Reset chance
            return {"encounter": True}
        # Roll for item discovery
        if random.random() < ITEM_FIND_CHANCE:
            loot = random.choice([HealingPotion(), GoldPile(randint(5, 20))])

            # Non-storable items like GoldPile are used immediately.
            if not loot.can_store:
                loot.use(self.player)
                add_to_log(self.log, f"+{loot.amount} Gold!")
            else:
                self.player.add_item(loot)
                add_to_log(self.log, f"Found a {loot.name}.")
        else:
            add_to_log(self.log, "You found nothing.")

        # Increment encounter chance
        self.encounter_chance = min(1.0, self.encounter_chance + self.step)
        self.consecutive_turns += 1
        return {"encounter": False}

    def render(self):
        """
        Renders the exploration state.
        """
        self.screen.fill(config.BG_COLOR)

        inventory_pos = (config.SCREEN_WIDTH - 150, config.SCREEN_HEIGHT - 110)
        UI.render_inventory(self.screen, self.player.inventory, pos=inventory_pos)

        # Display player health
        player_health_spec = HealthBarSpec(
            *config.EXPLORE_PLAYER_HEALTH_POS,
            current=self.player.health,
            max_val=self.player.max_health,
            color=config.PLAYER_HEALTH_COLOR,
            label="Player"
        )
        UI.draw_health_bar(self.screen, player_health_spec)

        # Gold display
        UI.display_text(
            self.screen,
            f"Gold: {StateManager.gold}",
            config.EXPLORE_GOLD_POS,
            font_size=config.LARGE_FONT_SIZE,
            color=config.TEXT_COLOR
        )

        # Display instructions
        instructions = ["(S)earch"]
        if self.player.inventory:
            instructions.append("(I)tem")
        UI.display_text(
            self.screen, ", ".join(instructions),
            config.EXPLORE_INSTRUCTIONS_POS,
            font_size=config.MEDIUM_FONT_SIZE,
            color=config.UI_ACCENT_COLOR
        )

        # Display encounter chance
        UI.display_text(
            self.screen,
            f"Encounter Chance: {self.encounter_chance:.2f}",
            config.EXPLORE_ENCOUNTER_CHANCE_POS,
            font_size=config.MEDIUM_FONT_SIZE
        )

        if self.item_menu_open:
            UI.render_item_menu(self.screen, self.player)

        # Display log messages
        UI.render_explore_log(self.screen, self.log)
