class Game:
    def __init__(self, screen):
        self.screen = screen
        self.player_turn = True
        self.player = None
        self.enemy = None

    def setup(self):
        from player import Player
        from enemy import Enemy
        
        self.player = Player("Hero", 100, 20)
        self.enemy = Enemy("Goblin", 80, 15)

    def player_action(self):
        if self.player_turn:
            damage, crit, miss = self.player.attack(self.enemy)
            if miss:
                self.last_action = "Player missed!"
            elif crit:
                self.last_action = f"Critical hit! Player deals {damage} damage."
            else:
                self.last_action = f"Player deals {damage} damage."
            self.player_turn = False

    def enemy_action(self):
        if not self.player_turn:
            damage, crit, miss = self.enemy.attack(self.player)
            if miss:
                self.last_action = "Enemy missed!"
            elif crit:
                self.last_action = f"Critical hit! Enemy deals {damage} damage."
            else:
                self.last_action = f"Enemy deals {damage} damage."
            self.player_turn = True

    def update(self):
        if self.player.health <= 0:
            print("Player has been defeated!")
            return False
        elif self.enemy.health <= 0:
            print("Enemy has been defeated!")
            return False
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
        player_max = self.player.health
        enemy_max = self.enemy.health
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    action_ready = True
            if not running:
                break
            self.screen.fill((30, 30, 60))  # Dark blue background
            # Draw health bars
            self.draw_health_bar(50, 60, self.player.health, player_max, (0,200,0), "Player")
            self.draw_health_bar(50, 160, self.enemy.health, enemy_max, (200,0,0), "Enemy")
            # Instructions
            display_text(self.screen, "Press SPACE to attack", (50, 250), font_size=28, color=(200,200,200))
            # Last action
            if self.last_action:
                display_text(self.screen, self.last_action, (50, 320), font_size=32, color=(255, 215, 0))
            pygame.display.flip()
            if action_ready:
                if self.player_turn:
                    self.player_action()
                else:
                    self.enemy_action()
                if not self.update():
                    pygame.time.wait(1500)  # Pause to show result
                    break
                action_ready = False
            clock.tick(60)
        pygame.quit()