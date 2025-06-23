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
from ..states.victory import VictoryState
from ..states.game_over import GameOverState
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
        self.meta = EncounterMeta(score=0, encounter_index=0)

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
            raw_events = signals["raw_events"]

            if signals["quit"]:
                running = False

            # --- State-specific Logic & Rendering ---
            current_game_state = self.state_manager.get_state()

            if current_game_state == GameState.BATTLE:
                result = self.state_obj.update(signals)
                if result['status'] == 'VICTORY':
                    self.meta.score += 1
                    self.meta.encounter_index += 1
                    self.state_obj = VictoryState(self.screen, self.player, self.meta, self.state_obj.battle_log)
                    self.state_manager.set_state(GameState.VICTORY)
                elif result['status'] == 'FLEE_SUCCESS':
                    self.meta.reset()
                    self.state_obj = ExploreState(self.screen, self.player)
                    self.state_manager.set_state(GameState.EXPLORE)
                elif result['status'] == 'GAME_OVER':
                    self.state_obj = GameOverState(self.screen, self.player, self.meta, self.state_obj.battle_log)
                    self.state_manager.set_state(GameState.GAME_OVER)

            elif current_game_state == GameState.VICTORY:
                status = self.state_obj.handle_events(raw_events)
                if status == "TO_SHOP":
                    self.state_obj = ShopState(self.screen, self.player)
                    self.state_manager.set_state(GameState.SHOP)

            elif current_game_state == GameState.GAME_OVER:
                status = self.state_obj.handle_events(raw_events)
                if status == "RESTART":
                    self.state_manager.reset()
                    self.__init__()  # Re-initialize the game
                    return self.run()
                elif status == "QUIT":
                    running = False

            elif current_game_state == GameState.EXPLORE:
                result = self.state_obj.update(signals)
                if result and result.get("encounter"):
                    self.state_manager.set_state(GameState.BATTLE)
                    enemy = Enemy(encounter_index=self.meta.encounter_index)
                    self.state_obj = BattleState(self.screen, self.player, enemy, self.meta)

            elif current_game_state == GameState.SHOP:
                result = self.state_obj.update(signals)
                if result and result.get("next_state") == "EXPLORE":
                    self.state_obj = ExploreState(self.screen, self.player)
                    self.state_manager.set_state(GameState.EXPLORE)

            # All states now have a consistent render method
            self.state_obj.render(self.screen)

            pygame.display.flip()
            self.clock.tick(config.FPS)

        pygame.quit()
