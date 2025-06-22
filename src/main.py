import pygame
import config
from state import GameState, StateManager
from battle import Battle
from explore import ExploreState
from events import process_events
from player import Player
from enemy import Enemy

class GameManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption(config.GAME_TITLE)
        self.clock = pygame.time.Clock()
        
        # Initialise State
        self.state_manager = StateManager()
        
        # Initialise Player and Enemy for the first battle
        self.player = Player()
        self.enemy = Enemy(wave=0)
        
        # Score and wave are managed here
        self.score = 0
        self.wave = 0

        # Create the initial battle state
        self.state_obj = Battle(self.screen, self.player, self.enemy, self.score, self.wave)
        self.state_manager.set_state(GameState.BATTLE)

    def run(self):
        running = True
        while running:
            signals = process_events()

            if signals["quit"]:
                running = False

            current_state = self.state_manager.get_state()
            
            # --- State-independent Input Handling ---
            if signals["enter_explore"] and current_state == GameState.BATTLE:
                self.state_obj = ExploreState(self.player)
                self.state_manager.set_state(GameState.EXPLORE)
                print("Switched to EXPLORE state")

            # --- State-specific Logic & Rendering ---
            if self.state_manager.get_state() == GameState.BATTLE:
                result = self.state_obj.update(signals)
                self.state_obj.render()
                
                if result['status'] == 'VICTORY':
                    self.score += 1
                    self.wave += 1
                    # Persist player health and potions across battles
                    self.player.health = self.state_obj.player.health
                    self.player.potions = self.state_obj.player.potions
                    self.enemy = Enemy(wave=self.wave)
                    self.state_obj = Battle(self.screen, self.player, self.enemy, self.score, self.wave)
                    print("New battle starts!")

                elif result['status'] == 'GAME_OVER':
                    running = False
                    print("Game Over!")

            elif self.state_manager.get_state() == GameState.EXPLORE:
                result = self.state_obj.update(signals)
                if result is False:
                    self.state_manager.set_state(GameState.BATTLE)
                    self.enemy = Enemy(wave=self.wave)
                    self.state_obj = Battle(self.screen, self.player, self.enemy, self.score, self.wave)
                elif result and result.get("encounter"):
                    self.state_manager.set_state(GameState.BATTLE)
                    self.enemy = Enemy(wave=self.wave)
                    self.state_obj = Battle(self.screen, self.player, self.enemy, self.score, self.wave)
                else:
                    self.state_obj.render(self.screen)
            
            pygame.display.flip()
            self.clock.tick(config.FPS)

        pygame.quit()

def main():
    """Initialises and runs the game."""
    game_manager = GameManager()
    game_manager.run()

if __name__ == "__main__":
    main()