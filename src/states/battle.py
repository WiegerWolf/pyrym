import pygame
import random
import random
from src.core.game_state import GameState
from src.entities import Player
from src.enemy import Enemy
from src.core.ui import render_battle_screen
from src.utils import add_to_log
from src.core import events
from src.items import HealingPotion
import src.config as config


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
        self.add_to_log(f"A wild {self.enemy.name} appears!")


    def player_action(self, action='attack'):
        if self.player_turn:
            if action == 'attack':
                damage, crit, miss = self.player.attack_action(self.enemy)
                msg = ("Player missed!" if miss else
                       f"Critical hit! Player deals {damage} damage." if crit else
                       f"Player deals {damage} damage.")
                self.add_to_log(msg)
                self.last_action = msg
            elif action == 'heal':
                if not self.player.has_potion():
                    self.add_to_log("No potions left!")
                    # Important: Do not flip player_turn, so the player can try another action
                    return

                heal_amount = self.player.use_potion()
                if heal_amount > 0:
                    potion_count = sum(1 for item in self.player.inventory if isinstance(item, HealingPotion))
                    msg = f"Player uses potion for {heal_amount} HP! ({potion_count} left)"
                else:
                    # This case should not be reachable due to the has_potion() check
                    msg = "No potions left!"
                self.add_to_log(msg)
                self.last_action = msg
            elif action == 'defend':
                self.player.defend()
                msg = "Player is defending! Next enemy attack is halved."
                self.add_to_log(msg)
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
            self.add_to_log(msg)
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

        return self.check_battle_status()


    def check_battle_status(self):
        if self.enemy.health <= 0:
            return {"status": "VICTORY"}
        if self.player.health <= 0:
            self.add_to_log("Player has been defeated!")
            return {'status': 'GAME_OVER'}
        return {'status': 'ONGOING'}


    def render(self):
        """Renders the battle screen."""
        UI.render_battle_screen(self.screen, self)