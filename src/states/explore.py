"""
explore.py
Manages the exploration state where the player can find items or trigger encounters.
"""
import random
from random import randint

from .. import config
from ..config import BASE_ENCOUNTER_CHANCE, ENCOUNTER_INCREMENT, ITEM_FIND_CHANCE
from ..items import HealingPotion, GoldPile

class ExploreState:
    """
    Manages the exploration phase of the game, where the player can find items
    or trigger encounters.
    """
    def __init__(self, player):
        """
        Initializes the exploration state.

        Args:
            player: The player character instance.
        """
        self.player = player
        self.base_chance = BASE_ENCOUNTER_CHANCE
        self.step = ENCOUNTER_INCREMENT
        self.consecutive_turns = 0
        self.encounter_chance = self.base_chance

    def update(self, signals):
        """
        Updates the exploration state based on player input.

        Args:
            signals (dict): A dictionary of input signals.

        Returns:
            dict or bool: A dictionary with encounter/potion info, False to return to battle,
                           or None if no action is taken.
        """
        from ..core import UI

        if signals.get("attack"):  # Continue exploring
            return self._explore_turn()
        elif signals.get("p") and self.player.has_potion():  # Use potion
            heal_amount = self.player.use_potion()
            if heal_amount > 0:
                UI.notify(f"You used a healing potion and healed for {heal_amount} HP.")
                return {"used_potion": True}
            return None
        return None


    def _explore_turn(self):
        """
        Handles the logic for a single turn of exploration.

        Returns:
            dict: A dictionary indicating if an encounter occurred.
        """
        from ..core import UI
        if random.random() < self.encounter_chance:
            self.encounter_chance = self.base_chance  # Reset chance
            return {"encounter": True}
        else:
            # Roll for item discovery
            if random.random() < ITEM_FIND_CHANCE:
                item = random.choice([HealingPotion(20), GoldPile(randint(5, 20))])
                self.player.add_item(item)
                UI.notify(f"Found {item}")

            # Increment encounter chance
            self.encounter_chance = min(1.0, self.encounter_chance + self.step)
            self.consecutive_turns += 1
            return {"encounter": False}

    def render(self, surface):
        """
        Renders the exploration state.

        Args:
            surface: The surface to draw on.
        """
        from ..core import UI
        surface.fill(config.BG_COLOR)

        UI.render_inventory(surface, self.player.inventory, pos=(10,10))

        # Display player health
        UI.draw_health_bar(surface, *config.EXPLORE_PLAYER_HEALTH_POS, self.player.health, self.player.max_health, config.PLAYER_HEALTH_COLOR, "Player")

        # Display instructions
        instructions = ["Space: Continue"]
        if self.player.has_potion():
            instructions.append("P: Use Potion")
        UI.display_text(surface, ", ".join(instructions), config.EXPLORE_INSTRUCTIONS_POS, font_size=config.MEDIUM_FONT_SIZE, color=config.UI_ACCENT_COLOR)

        # Display encounter chance
        UI.display_text(surface, f"Encounter Chance: {self.encounter_chance:.2f}", config.EXPLORE_ENCOUNTER_CHANCE_POS, font_size=config.MEDIUM_FONT_SIZE, color=config.TEXT_COLOR)

        # Display last message
        message = UI.get_last_message()
        if message:
            UI.display_text(surface, message, config.EXPLORE_MESSAGE_POS, font_size=config.MEDIUM_FONT_SIZE, color=config.TEXT_COLOR)
