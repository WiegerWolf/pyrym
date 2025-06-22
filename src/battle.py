import pygame
import random
import config
from player import Player
from enemy import Enemy
from ui import render_battle_screen
from utils import add_to_log
from events import process_events

class Battle:
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


    def add_to_log(self, message):
        add_to_log(self.battle_log, message)

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
                heal_amount = self.player.heal_action()
                if heal_amount > 0:
                    msg = f"Player uses potion for {heal_amount} HP! ({self.player.potions} left)"
                else:
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
        if self.player_turn:
            if signals.get("player_action_ready"):
                self.player_action(signals["player_action_type"])
            elif signals.get("flee"):
                if random.random() < config.FLEE_SUCCESS_PROB:
                    return {"status": "FLEE_SUCCESS"}
                else:
                    self.add_to_log("Player failed to flee!")
                    self.player_turn = False
    
        if self.enemy.health <= 0:
            return {"status": "VICTORY"}
        
        if not self.player_turn:
            self.enemy_action()
            if self.player.health <= 0:
                self.add_to_log("Player has been defeated!")
                return {'status': 'GAME_OVER'}
    
        return {'status': 'ONGOING'}

    def render(self):
        """Renders the battle screen."""
        render_battle_screen(self.screen, self)

    # Note: The main run() method with its own loop is now removed.
    # The main game loop in main.py will call update() and render().