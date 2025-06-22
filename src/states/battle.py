"""
battle.py
Manages the state of a battle encounter.
"""
import random

from .. import config
from ..core.ui import render_battle_screen
from ..items import HealingPotion
from ..utils import add_to_log, EncounterMeta


class BattleState:
    """Manages the state of a single battle encounter."""

    def __init__(self, screen, player, enemy, encounter_meta: EncounterMeta):
        self.screen = screen
        self.player = player
        self.enemy = enemy
        self.meta = encounter_meta

        self.player_turn = True
        self.battle_log = []

        # Reset entities for battle
        self.player.reset()
        # self.enemy.reset() # TODO: Add reset to Enemy
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
                damage, crit, miss = self.player.attack_action(self.enemy)
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
            self.player_turn = False

    def enemy_action(self):
        """Executes the enemy's action and returns the message."""
        if self.player_turn:
            return

        # AI: Decide whether to defend
        should_defend = (
            self.enemy.health < self.enemy.max_health * 0.35
            and random.random() < 0.25
        )

        if should_defend:
            self.enemy.defend()
            add_to_log(self.battle_log, f"{self.enemy.name} is defending!")
        else:
            # Attack action
            damage, crit, miss = self.enemy.attack_action(self.player)
            if miss:
                msg = f"{self.enemy.name} missed!"
            elif crit:
                msg = f"Critical hit! {self.enemy.name} deals {damage} damage."
            else:
                msg = f"{self.enemy.name} deals {damage} damage."
            add_to_log(self.battle_log, msg)

        self.player_turn = True

    def update(self, signals):
        """
        Runs one frame of battle logic. Returns a status dictionary.
        """
        if not self.player_turn and self.enemy.health > 0:
            self.enemy_action()

        # Handle button presses for actions
        if self.player_turn:
            action_taken = None
            if signals["attack"]:
                action_taken = 'attack'
            elif signals["defend"]:
                action_taken = 'defend'
            elif signals["heal"]:
                action_taken = 'heal'

            if action_taken:
                self.player_action(action_taken)
            elif signals["flee"]:
                if random.random() <= config.FLEE_SUCCESS_PROB:
                    return {"status": "FLEE_SUCCESS"}
                add_to_log(self.battle_log, "Flee failed!")
                self.player_turn = False

        return self.check_battle_status()

    def check_battle_status(self):
        """Checks the status of the battle (win, lose, ongoing)."""
        if self.enemy.health <= 0:
            return {"status": "VICTORY"}
        if self.player.health <= 0:
            add_to_log(self.battle_log, "Player has been defeated!")
            return {'status': 'GAME_OVER'}
        return {'status': 'ONGOING'}

    def render(self):
        """Renders the battle screen."""
        render_battle_screen(self.screen, self)
