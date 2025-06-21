class Game:
    def __init__(self, screen):
        self.screen = screen
        self.player_turn = True
        self.player = None
        self.enemy = None

    def setup_enemy(self, wave):
        from enemy import Enemy
        # Increase enemy stats with each wave
        base_health = 80 + wave * 20
        base_attack = 15 + wave * 3
        self.enemy_max_health = base_health
        return Enemy(f"Goblin Lv.{wave+1}", base_health, base_attack)

    def setup(self):
        from player import Player
        self.player = Player("Hero", 100, 20)
        self.wave = 0
        self.score = 0
        self.enemy = self.setup_enemy(self.wave)
        self.player_max_health = self.player.health
        self.potions = 0  # Healing potions
        self.defending = False
        self.battle_log = []  # Store last 3 actions

    def add_to_log(self, message):
        self.battle_log.append(message)
        if len(self.battle_log) > 5:
            self.battle_log.pop(0)

    def player_action(self, action='attack'):
        if self.player_turn:
            if action == 'attack':
                damage, crit, miss = self.player.attack(self.enemy)
                if miss:
                    msg = "Player missed!"
                elif crit:
                    msg = f"Critical hit! Player deals {damage} damage."
                else:
                    msg = f"Player deals {damage} damage."
                self.add_to_log(msg)
                self.last_action = msg
            elif action == 'heal':
                if self.potions > 0:
                    heal_amount = min(20, self.player_max_health - self.player.health)
                    self.player.health += heal_amount
                    self.potions -= 1
                    msg = f"Player uses potion for {heal_amount} HP! ({self.potions} left)"
                else:
                    msg = "No potions left!"
                self.add_to_log(msg)
                self.last_action = msg
            elif action == 'defend':
                self.defending = True
                msg = "Player is defending! Next enemy attack is halved."
                self.add_to_log(msg)
                self.last_action = msg
            self.player_turn = False

    def enemy_action(self):
        if not self.player_turn:
            damage, crit, miss = self.enemy.attack(self.player)
            if self.defending:
                damage = damage // 2
                self.player.health += damage  # Undo full damage
                self.player.health -= damage  # Apply halved damage
                self.defending = False
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
        import pygame  # Ensure pygame is available
        import random
        if self.player.health <= 0:
            print("Player has been defeated!")
            return False
        elif self.enemy.health <= 0:
            self.score += 1
            self.wave += 1
            # 50% chance to drop a potion
            if random.random() < 0.5:
                self.potions += 1
                msg = f"Enemy defeated! Potion dropped! New enemy approaches!"
            else:
                msg = f"Enemy defeated! New enemy approaches!"
            self.add_to_log(msg)
            self.last_action = msg
            self.enemy = self.setup_enemy(self.wave)
            pygame.time.wait(1000)
        return True

    def draw_health_bar(self, x, y, current, max_health, color, label):
        import pygame
        bar_width = 200
        bar_height = 30
        fill = int(bar_width * (current / max_health))
        outline_rect = pygame.Rect(x, y, bar_width, bar_height)
        fill_rect = pygame.Rect(x, y, fill, bar_height)
        pygame.draw.rect(self.screen, color, fill_rect)
        pygame.draw.rect(self.screen, (255,255,255), outline_rect, 2)
        from utils import display_text
        display_text(self.screen, label, (x, y - 28), font_size=32, color=color)
        display_text(self.screen, f"{current} / {max_health}", (x + bar_width + 10, y), font_size=28, color=(255,255,255))

    def run(self):
        import pygame
        from utils import display_text
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
            self.screen.fill((30, 30, 60))  # Dark blue background
            # Draw health bars
            self.draw_health_bar(50, 60, self.player.health, self.player_max_health, (0,200,0), "Player")
            self.draw_health_bar(50, 160, self.enemy.health, self.enemy_max_health, (200,0,0), self.enemy.name)
            # Score and wave
            display_text(self.screen, f"Score: {self.score}", (400, 30), font_size=32, color=(255,255,255))
            display_text(self.screen, f"Wave: {self.wave+1}", (400, 70), font_size=28, color=(255,255,255))
            # Instructions
            if self.player_turn:
                display_text(self.screen, "SPACE: Attack    P: Potion    D: Defend", (50, 250), font_size=28, color=(200,200,200))
            else:
                display_text(self.screen, "Enemy's turn...", (50, 250), font_size=28, color=(255,100,100))
            display_text(self.screen, f"Potions: {self.potions}", (50, 290), font_size=24, color=(100,255,100))
            # Battle log (last 3 actions, fading)
            log_colors = [(255, 215, 0), (200, 200, 200), (120, 120, 120), (80, 80, 80), (50, 50, 50)]
            for i, msg in enumerate(reversed(self.battle_log)):
                display_text(self.screen, msg, (50, 340 + i*32), font_size=28, color=log_colors[i])
            pygame.display.flip()
            if self.player_turn and action_ready:
                self.player_action(player_action_type)
                action_ready = False
            elif not self.player_turn:
                pygame.time.wait(700)  # Short pause for enemy turn
                self.enemy_action()
            if not self.update():
                pygame.time.wait(1500)  # Pause to show result
                break
            clock.tick(60)
        pygame.quit()