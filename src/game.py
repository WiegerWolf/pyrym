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
        self.setup()
        while True:
            self.player_action()
            if not self.update():
                break
            self.enemy_action()
            if not self.update():
                break