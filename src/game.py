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
            self.player.attack(self.enemy)
            self.player_turn = False

    def enemy_action(self):
        if not self.player_turn:
            self.enemy.attack(self.player)
            self.player_turn = True

    def update(self):
        if self.player.health <= 0:
            print("Player has been defeated!")
            return False
        elif self.enemy.health <= 0:
            print("Enemy has been defeated!")
            return False
        return True

    def run(self):
        import pygame
        from utils import display_text
        self.setup()
        clock = pygame.time.Clock()
        running = True
        action_ready = True  # Wait for player input
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    action_ready = True
            if not running:
                break
            self.screen.fill((0, 0, 0))  # Clear screen (black)
            # Display player and enemy health
            display_text(self.screen, f"Player: {self.player.health}", (50, 50))
            display_text(self.screen, f"Enemy: {self.enemy.health}", (50, 100))
            display_text(self.screen, "Press SPACE to attack", (50, 200), font_size=24, color=(200,200,200))
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