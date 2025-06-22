"""
battle.py
Manages the state of a battle encounter.
"""
import random

from .. import config
from ..core.ui import render_battle_screen
from ..items import HealingPotion
from ..utils import add_to_log


class BattleState:
    def __init__(self, screen, player, enemy, score, wave):
        self.screen = screen
        self.player = player
        self.enemy = enemy
        self.score = score
        self.wave = wave

        self.player_max_health = player.max_health
        self.enemy_max_health = enemy.health

        self.player_turn = True
        self.battle_log = []
        add_to_log(self.battle_log, f"A wild {self.enemy.name} appears!")


    def player_action(self, action='attack'):
        """Executes a player action (attack, heal, or defend)."""
        if self.player_turn:
            if action == 'attack':
                damage, crit, miss = self.player.attack_action(self.enemy)
                msg = ("Player missed!" if miss else
                       f"Critical hit! Player deals {damage} damage." if crit else
                       f"Player deals {damage} damage.")
                add_to_log(self.battle_log, msg)
                self.last_action = msg
            elif action == 'heal':
                if not self.player.has_potion():
                    add_to_log(self.battle_log, "No potions left!")
                    # Important: Do not flip player_turn, so the player can try another action
                    return

                heal_amount = self.player.use_potion()
                if heal_amount > 0:
                    potion_count = sum(1 for item in self.player.inventory if isinstance(item, HealingPotion))
                    msg = f"Player uses potion for {heal_amount} HP! ({potion_count} left)"
                else:
                    # This case should not be reachable due to the has_potion() check
                    msg = "No potions left!"
                add_to_log(self.battle_log, msg)
                self.last_action = msg
            elif action == 'defend':
                self.player.defend()
                msg = "Player is defending! Next enemy attack is halved."
                add_to_log(self.battle_log, msg)
                self.last_action = msg
            self.player_turn = False

    def enemy_action(self):
        if not self.player_turn:
            damage, crit, miss = self.enemy.attack_action(self.player)
            was_defending = self.player.is_defending

            if miss:
                msg = "Enemy missed!"
            elif crit:
                msg = f"Critical hit! Enemy deals {damage} damage."
            elif was_defending:
                msg = f"Enemy attacks, but damage is reduced! ({damage} damage)"
            else:
                msg = f"Enemy deals {damage} damage."
            add_to_log(self.battle_log, msg)
            self.last_action = msg
            self.player_turn = True

    def update(self, signals):
        """
        Runs one frame of battle logic. Returns a status dictionary.
        """
        if not self.player_turn and self.enemy.health > 0:
            self.enemy_action()

        # Handle button presses for actions
        if self.player_turn:
            if signals["attack"]:
                self.player_action('attack')
            elif signals["defend"]:
                self.player_action('defend')
            elif signals["heal"]:
                self.player_action('heal')
            elif signals["flee"]:
                # Roll for flee success based on configured probability
                if random.random() <= config.FLEE_SUCCESS_PROB:
                    return {"status": "FLEE_SUCCESS"}
                add_to_log(self.battle_log, "Flee failed!")
                self.last_action = "Flee failed!"
                # Failed flee consumes the player's turn
                self.player_turn = False

        return self.check_battle_status()


    def check_battle_status(self):
        if self.enemy.health <= 0:
            return {"status": "VICTORY"}
        if self.player.health <= 0:
            add_to_log(self.battle_log, "Player has been defeated!")
            return {'status': 'GAME_OVER'}
        return {'status': 'ONGOING'}


    def render(self):
        """Renders the battle screen."""
        render_battle_screen(self.screen, self)
