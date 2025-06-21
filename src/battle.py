import pygame
import random
import config
from player import Player
from enemy import Enemy
from ui import display_text, draw_health_bar
from utils import add_to_log

class Battle:
    def __init__(self, screen):
        self.screen = screen
        self.player_turn = True
        self.player = None
        self.enemy = None

    def setup_enemy(self, wave):
        from enemy import Enemy
        # Slower enemy scaling
        base_health = config.ENEMY_BASE_HEALTH + wave * config.ENEMY_HEALTH_SCALING
        base_attack = config.ENEMY_BASE_ATTACK + wave * config.ENEMY_ATTACK_SCALING
        self.enemy_max_health = base_health
        return Enemy(f"Goblin Lv.{wave+1}", base_health, base_attack)

    def setup(self):
        from player import Player
        self.player = Player("Hero", config.PLAYER_BASE_HEALTH, config.PLAYER_BASE_ATTACK)
        self.player.is_defending = False
        self.wave = 0
        self.score = 0
        self.enemy = self.setup_enemy(self.wave)
        self.enemy.is_defending = False
        self.player_max_health = self.player.health
        self.potions = 0  # Healing potions
        self.defending = False
        self.battle_log = []  # Store last 3 actions

    def add_to_log(self, message):
        add_to_log(self.battle_log, message)

    def player_action(self, action='attack'):
        if self.player_turn:
            if action == 'attack':
                damage, crit, miss = self.player.attack(self.enemy)
                msg = ("Player missed!" if miss else
                       f"Critical hit! Player deals {damage} damage." if crit else
                       f"Player deals {damage} damage.")
                self.add_to_log(msg)
                self.last_action = msg
            elif action == 'heal':
                if self.potions > 0:
                    heal_amount = self.player.heal(self.player_max_health, config.POTION_HEAL_AMOUNT)
                    self.potions -= 1
                    msg = f"Player uses potion for {heal_amount} HP! ({self.potions} left)"
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
            damage, crit, miss = self.enemy.attack(self.player)
            if getattr(self.player, 'is_defending', False):
                damage = damage // 2
                self.player.health += damage  # Undo full damage
                self.player.health -= damage  # Apply halved damage
                self.player.reset_defend()
                msg = f"Enemy attacks, but damage is halved! ({damage} damage)"
            else:
                if miss:
                    msg = "Enemy missed!"
                elif crit:
                    msg = f"Critical hit! Enemy deals {damage} damage."
                else:
                    msg = f"Enemy deals {damage} damage."
            self.add_to_log(msg)
            self.last_action = msg
            self.player_turn = True

    def update(self):
        if self.player.health <= 0:
            print("Player has been defeated!")
            return False
        elif self.enemy.health <= 0:
            self.score += 1
            self.wave += 1
            # 50% chance to drop a potion
            if random.random() < config.POTION_DROP_CHANCE:
                self.potions += 1
                msg = f"Enemy defeated! Potion dropped! New enemy approaches!"
            else:
                msg = f"Enemy defeated! New enemy approaches!"
            self.add_to_log(msg)
            self.last_action = msg
            self.enemy = self.setup_enemy(self.wave)
            self.player_turn = True  # Player gets first move on new enemy
            pygame.time.wait(config.END_OF_BATTLE_PAUSE_MS)
        return True

    def run(self):
        self.setup()
        self.last_action = ""
        clock = pygame.time.Clock()
        running = True
        action_ready = True  # Wait for player input
        player_action_type = 'attack'
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if self.player_turn and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        action_ready = True
                        player_action_type = 'attack'
                    if event.key == pygame.K_p:
                        action_ready = True
                        player_action_type = 'heal'
                    if event.key == pygame.K_d:
                        action_ready = True
                        player_action_type = 'defend'
            if not running:
                break
            self.screen.fill(config.BG_COLOR)  # Dark blue background
            # Draw health bars
            draw_health_bar(self.screen, 50, 60, self.player.health, self.player_max_health, config.PLAYER_HEALTH_COLOR, "Player")
            draw_health_bar(self.screen, 50, 160, self.enemy.health, self.enemy_max_health, config.ENEMY_HEALTH_COLOR, self.enemy.name)
            # Score and wave
            display_text(self.screen, f"Score: {self.score}", (400, 30), font_size=config.LARGE_FONT_SIZE, color=config.TEXT_COLOR)
            display_text(self.screen, f"Wave: {self.wave+1}", (400, 70), font_size=config.MEDIUM_FONT_SIZE, color=config.TEXT_COLOR)
            # Instructions
            if self.player_turn:
                display_text(self.screen, "SPACE: Attack    P: Potion    D: Defend", (50, 250), font_size=config.MEDIUM_FONT_SIZE, color=config.UI_ACCENT_COLOR)
            else:
                display_text(self.screen, "Enemy's turn...", (50, 250), font_size=config.MEDIUM_FONT_SIZE, color=config.ENEMY_TURN_COLOR)
            display_text(self.screen, f"Potions: {self.potions}", (50, 290), font_size=config.SMALL_FONT_SIZE, color=config.POTION_COLOR)
            # Battle log (last 5 actions, fading)
            for i, msg in enumerate(reversed(self.battle_log)):
                display_text(self.screen, msg, (50, 340 + i*32), font_size=config.MEDIUM_FONT_SIZE, color=config.LOG_COLORS[i])
            pygame.display.flip()
            if self.player_turn and action_ready:
                self.player_action(player_action_type)
                action_ready = False
            elif not self.player_turn:
                pygame.time.wait(config.ENEMY_TURN_PAUSE_MS)  # Short pause for enemy turn
                self.enemy_action()
            if not self.update():
                pygame.time.wait(config.GAME_OVER_PAUSE_MS)  # Pause to show result
                return None # End the battle state
            clock.tick(60)
        return None # Explicitly return None on window close