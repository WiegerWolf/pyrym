"""
explore.py
Manages the exploration state where the player can find items or trigger encounters.
"""
import random
from random import randint

from .. import config
from ..config import BASE_ENCOUNTER_CHANCE, ENCOUNTER_INCREMENT, ITEM_FIND_CHANCE
from ..core.ui import UI
from ..items import HealingPotion, GoldPile
from ..utils import HealthBarSpec


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
        self.base_chance = BASE_ENCOUNTER_CHANCE
        self.step = ENCOUNTER_INCREMENT
        self.consecutive_turns = 0
        self.encounter_chance = self.base_chance

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

        Args:
            signals (dict): A dictionary of input signals.

        Returns:
            dict or bool: A dictionary with encounter/potion info, or None.
        """
        if signals.get("search"):  # Continue exploring
            return self._explore_turn()
        if signals.get("use_item") and self.player.inventory:
            # This is a placeholder for a proper item menu in explore mode
            # For now, we'll just use the first item.
            used_item = self.player.use_item(0)
            if used_item:
                UI.notify(used_item["message"])
                return {"used_item": True}
            return None
        if signals.get("cheat_gold"):  # Cheat for gold
            from src.core.game_state import StateManager
            StateManager.adjust_gold(10)
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
                result = loot.use(self.player)
                UI.notify(f"+{loot.amount} Gold!")
            else:
                self.player.add_item(loot)
                UI.notify(f"Found a {loot.name}.")

        # Increment encounter chance
        self.encounter_chance = min(1.0, self.encounter_chance + self.step)
        self.consecutive_turns += 1
        return {"encounter": False}

    def render(self):
        """
        Renders the exploration state.
        """
        self.screen.fill(config.BG_COLOR)

        UI.render_inventory(self.screen, self.player.inventory, pos=(10, 10))

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
        from src.core.game_state import StateManager
        UI.display_text(
            self.screen,
            f"Gold: {StateManager.gold}",
            config.EXPLORE_GOLD_POS,
            font_size=config.LARGE_FONT_SIZE,
            color=config.TEXT_COLOR
        )

        # Display instructions
        instructions = ["(S)earch", "(G)old Cheat"]
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

        # Display last message
        message = UI.get_last_message()
        if message:
            UI.display_text(
                self.screen,
                message,
                config.EXPLORE_MESSAGE_POS,
                font_size=config.MEDIUM_FONT_SIZE
            )
