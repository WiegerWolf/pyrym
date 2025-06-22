"""
game.py
Core game loop and state management.
"""
import pygame

# pylint: disable=no-member
from .. import config
from .game_state import GameState, StateManager
from ..states.battle import BattleState
from ..states.explore import ExploreState
from .events import process_events
from ..entities import Player
from ..entities import Enemy

class Game:
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

        # Create the initial explore state
        self.state_obj = ExploreState(self.player)
        self.state_manager.set_state(GameState.EXPLORE)

    def run(self):
        """Runs the main game loop."""
        running = True
        while running:
            signals = process_events()

            if signals["quit"]:
                running = False

            current_state = self.state_manager.get_state()

            # --- State-specific Logic & Rendering ---
            if self.state_manager.get_state() == GameState.BATTLE:
                result = self.state_obj.update(signals)
                self.state_obj.render(self.screen)

                if result['status'] == 'VICTORY':
                    self.score += 1
                    self.state_obj = ExploreState(self.player)
                    self.state_manager.set_state(GameState.EXPLORE)

                elif result['status'] == 'FLEE_SUCCESS':
                    self.state_obj = ExploreState(self.player)
                    self.state_manager.set_state(GameState.EXPLORE)

                elif result['status'] == 'GAME_OVER':
                    running = False
                    print("Game Over!")

            elif self.state_manager.get_state() == GameState.EXPLORE:
                result = self.state_obj.update(signals)
                if result and result.get("encounter"):
                    self.state_manager.set_state(GameState.BATTLE)
                    self.enemy = Enemy(wave=self.wave)
                    self.state_obj = BattleState(self.screen, self.player, self.enemy, self.score, self.wave)
                else:
                    self.state_obj.render(self.screen)

            pygame.display.flip()
            self.clock.tick(config.FPS)

        pygame.quit()
