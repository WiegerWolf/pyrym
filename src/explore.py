import random
from random import randint

from src.items import HealingPotion, GoldPile

class ExploreState:
    """
    Manages the exploration phase of the game, where the player can find items
    or trigger encounters.
    """
    def __init__(self, player, base_chance=0.10, step=0.05):
        """
        Initializes the exploration state.

        Args:
            player: The player character instance.
            base_chance (float): The initial chance of an encounter.
            step (float): The amount to increase the encounter chance by each turn.
        """
        self.player = player
        self.base_chance = base_chance
        self.step = step
        self.consecutive_turns = 0
        self.encounter_chance = base_chance

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
            if random.random() < 0.3:
                item = random.choice([HealingPotion(20), GoldPile(randint(5, 20))])
                self.player.add_item(item)
                print(f"You found a {item.name}!") # Placeholder for now

            # Increment encounter chance
            self.encounter_chance = min(1.0, self.encounter_chance + self.step)
            self.consecutive_turns += 1
            return {"encounter": False}

    def render(self, surface):
        """
        Renders the exploration state. (Currently placeholder)

        Args:
            surface: The surface to draw on.
        """
        print("Exploring... C: Continue, B: Back to Battle, P: Use Potion")
        print(f"Encounter Chance: {self.encounter_chance:.2f}")