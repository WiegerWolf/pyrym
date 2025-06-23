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
from ..states.shop import ShopState
from .events import process_events
from ..entities import Player
from ..entities import Enemy
from ..items.items import HealingPotion, StaminaPotion
from ..utils import EncounterMeta


# pylint: disable=too-few-public-methods
class Game:
    """Manages the main game loop and state transitions."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption(config.GAME_TITLE)
        self.clock = pygame.time.Clock()

        self.state_manager = StateManager()
        self.player = Player()
        self.meta = EncounterMeta(score=0, wave=0)

        self.player.add_item(HealingPotion())
        self.player.add_item(StaminaPotion())

        # Create the initial explore state
        self.state_obj = ExploreState(self.screen, self.player)
        self.state_manager.set_state(GameState.EXPLORE)

    def run(self):
        """Runs the main game loop."""
        running = True
        while running:
            signals = process_events()

            if signals["quit"]:
                running = False

            # --- State-specific Logic & Rendering ---
            current_game_state = self.state_manager.get_state()

            if current_game_state == GameState.BATTLE:
                result = self.state_obj.update(signals)
                if result['status'] == 'VICTORY':
                    self.meta.score += 1
                    self.meta.wave += 1
                    # After victory, go to the shop
                    self.state_obj = ShopState(self.screen, self.player)
                    self.state_manager.set_state(GameState.SHOP)
                elif result['status'] == 'FLEE_SUCCESS':
                    self.meta.reset()  # Reset the 'fled' flag
                    self.state_obj = ExploreState(self.screen, self.player)
                    self.state_manager.set_state(GameState.EXPLORE)
                elif result['status'] == 'GAME_OVER':
                    running = False
                    print("Game Over!")

            elif current_game_state == GameState.EXPLORE:
                result = self.state_obj.update(signals)
                if result and result.get("encounter"):
                    self.state_manager.set_state(GameState.BATTLE)
                    enemy = Enemy(wave=self.meta.wave)
                    self.state_obj = BattleState(self.screen, self.player, enemy, self.meta)

            elif current_game_state == GameState.SHOP:
                result = self.state_obj.update(signals)
                if result and result.get("next_state") == "EXPLORE":
                    self.state_obj = ExploreState(self.screen, self.player)
                    self.state_manager.set_state(GameState.EXPLORE)

            # All states now have a consistent render method
            self.state_obj.render()

            pygame.display.flip()
            self.clock.tick(config.FPS)

        pygame.quit()
