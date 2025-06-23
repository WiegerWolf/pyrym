"""
battle.py
Manages the state of a battle encounter.
"""
import random

from .. import config
from ..core.ui import render_battle_screen, UI
from ..items.items import HealingPotion
from ..utils import add_to_log, EncounterMeta, handle_item_use


class BattleState:
    """Manages the state of a single battle encounter."""

    def __init__(self, screen, player, enemy, encounter_meta: EncounterMeta):
        self.screen = screen
        self.player = player
        self.enemy = enemy
        self.meta = encounter_meta
        self.item_menu_open = False

        self.player_turn = True
        self.battle_log = []

        # Reset entities for battle
        self.player.battle_reset()
        self.enemy.reset()
        add_to_log(self.battle_log, f"A wild {self.enemy.name} appears!")

    @property
    def player_max_health(self):
        """Returns the player's maximum health."""
        return self.player.max_health

    @property
    def enemy_max_health(self):
        """Returns the enemy's maximum health."""
        return self.enemy.max_health

    def player_action(self, action='attack'):
        """
        Executes a player action (attack, heal, or defend).
        Returns the action message for logging.
        """
        msg = ""  # Default message if no action is taken
        if self.player_turn:
            if action == 'attack':
                result = self.player.attack_action(self.enemy)
                if result.get("no_stamina"):
                    add_to_log(self.battle_log, "Too tired to attack!")
                    return  # Don't flip turn
                damage, crit, miss = result["damage"], result["crit"], result["miss"]
                msg = ("Player missed!" if miss else
                       f"Critical hit! Player deals {damage} damage." if crit else
                       f"Player deals {damage} damage.")
            elif action == 'heal':
                if not self.player.has_potion():
                    add_to_log(self.battle_log, "No potions left!")
                    return  # Don't flip turn
                heal_amount = self.player.use_potion()
                if heal_amount > 0:
                    potion_count = sum(1 for item in self.player.inventory
                                     if isinstance(item, HealingPotion))
                    msg = f"Player uses potion for {heal_amount} HP! ({potion_count} left)"
                else:
                    msg = "No potions left!"
            elif action == 'defend':
                self.player.defend()
                msg = "Player braces for the next attack, gaining 1 stamina."
            add_to_log(self.battle_log, msg)
            self.meta.turns += 1
            self.player_turn = False

    def enemy_action(self):
        """Executes the enemy's action and returns the message."""
        if self.player_turn:
            return

        # AI: Decide whether to defend
        should_defend = (
            self.enemy.stamina == 0 or
            (self.enemy.health < self.enemy.max_health * 0.35 and random.random() < 0.25)
        )

        if should_defend:
            self.enemy.defend()
            add_to_log(self.battle_log, f"{self.enemy.name} is defending!")
        else:
            # Attack action
            result = self.enemy.attack_action(self.player)
            damage, crit, miss = result["damage"], result["crit"], result["miss"]
            if miss:
                msg = f"{self.enemy.name} missed!"
            elif crit:
                msg = f"Critical hit! {self.enemy.name} deals {damage} damage."
            else:
                msg = f"{self.enemy.name} deals {damage} damage."
            add_to_log(self.battle_log, msg)
        self.meta.turns += 1
        self.player_turn = True

    def update(self, signals):
        """
        Runs one frame of battle logic. Returns a status dictionary.
        """
        if not self.player_turn and self.enemy.health > 0:
            self.enemy_action()

        if self.player_turn:
            if self.item_menu_open:
                self._handle_item_menu(signals)
            else:
                self._handle_player_actions(signals)

        return self.check_battle_status()

    def _handle_item_menu(self, signals):
        """Handle input when the item menu is open."""
        if signals.get("number_keys"):
            key = signals["number_keys"][0]
            result = handle_item_use(self.player, key, lambda msg: add_to_log(self.battle_log, msg))
            if result.get("success"):
                self.item_menu_open = False
                self.player_turn = False
        elif signals.get("use_item"):
            self.item_menu_open = False

    def _handle_player_actions(self, signals):
        """Handle player actions when the item menu is closed."""
        action_taken = None
        if signals["attack"]:
            action_taken = 'attack'
        elif signals["defend"]:
            action_taken = 'defend'
        elif signals["use_item"]:
            if self.player.inventory:
                self.item_menu_open = True
            else:
                add_to_log(self.battle_log, "Inventory is empty.")

        if action_taken:
            self.player_action(action_taken)
        elif signals["flee"]:
            if random.random() <= config.FLEE_SUCCESS_PROB:
                # This return is problematic for state management.
                # It should set a state that the main loop can check.
                # For now, we'll assume the caller handles this dict.
                # A better approach would be a state machine.
                self.meta.fled = True  # Set a flag instead of returning
            else:
                add_to_log(self.battle_log, "Flee failed!")
                self.player_turn = False

    def check_battle_status(self):
        """Checks the status of the battle (win, lose, ongoing)."""
        if self.meta.fled:
            return {"status": "FLEE_SUCCESS"}
        if self.enemy.health <= 0:
            self._handle_victory()
            return {"status": "VICTORY"}
        if self.player.health <= 0:
            add_to_log(self.battle_log, "Player has been defeated!")
            return {'status': 'GAME_OVER'}
        return {'status': 'ONGOING'}

    def _handle_victory(self):
        """Handles the logic for when the player wins a battle."""
        xp_award = max(1, (self.enemy.encounter_index + 1) * 10)
        gold_award = (self.enemy.encounter_index + 1) * 5
        self.player.gain_xp(xp_award)
        self.player.gain_gold(gold_award)
        self.meta.battles_won += 1
        add_to_log(self.battle_log, f"You have defeated the {self.enemy.name}!")
        add_to_log(self.battle_log, f"You gain {xp_award} XP and {gold_award} gold.")

        if random.random() < 0.10:
            potion = HealingPotion()
            self.player.add_item(potion)
            add_to_log(self.battle_log, f"The enemy dropped {potion.name}!")

    def render(self):
        """Renders the battle screen."""
        render_battle_screen(self.screen, self)
        if self.item_menu_open:
            UI.render_item_menu(self.screen, self.player)
