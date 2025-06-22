import random
from random import randint

from src.config import BASE_ENCOUNTER_CHANCE, ENCOUNTER_INCREMENT, ITEM_FIND_CHANCE
from src.items import HealingPotion, GoldPile
from src.ui import ui

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

        if signals.get("c"):  # Continue exploring
            return self._explore_turn()
        elif signals.get("b"):  # Back to battle
            self.encounter_chance = self.base_chance  # Reset encounter chance
            return False
        elif signals.get("p"):  # Use potion
            used_potion = self.player.use_potion()
            if used_potion:
                ui.notify("You used a healing potion")
            return {"used_potion": used_potion}
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
        else:
            # Roll for item discovery
            if random.random() < ITEM_FIND_CHANCE:
                item = random.choice([HealingPotion(20), GoldPile(randint(5, 20))])
                self.player.add_item(item)
                ui.notify(f"Found {item}")

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
        if not surface:
            print("Exploring... C: Continue, B: Back to Battle, P: Use Potion")
            print(f"Encounter Chance: {self.encounter_chance:.2f}")
            message = ui.get_last_message()
            if message:
                print(message)
        else:
            # Optional: Pygame rendering would go here
            message = ui.get_last_message()
            if message:
                print(message) # For now, still print to console