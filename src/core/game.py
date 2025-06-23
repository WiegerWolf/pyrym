"""
game.py
Core game loop and state management.
"""
import pygame

# pylint: disable=no-member,too-many-branches,inconsistent-return-statements
from .. import config
from .events import process_events
from .state_machine import StateMachine
from ..entities import Enemy, Player
from ..items.items import HealingPotion, StaminaPotion
from ..states.explore import ExploreState
from ..states.game_over import GameOverState
from ..utils import EncounterMeta


# pylint: disable=too-few-public-methods
class Game:
    """Manages the main game loop and state transitions."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption(config.GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # Core game data
        self.player = Player()
        self.meta = EncounterMeta(score=0, encounter_index=0)

        # Add starting items
        self.player.add_item(HealingPotion())
        self.player.add_item(StaminaPotion())

        #
        # Create the initial state machine
        # The machine will hold all shared resources that states need to access.
        #
        initial_state = ExploreState(self.player, self.meta, self.screen)
        self.machine = StateMachine(initial_state)
        # Give the state machine a reference back to the game
        # so that states can call `self.machine.game.end_game()` etc.
        self.machine.game = self

    def run(self):
        """Runs the main game loop."""
        while self.running:
            signals = process_events()
            raw_events = signals["raw_events"]

            if signals["quit"]:
                self.running = False

            if signals.get("restart"):
                self.restart_game()
                continue  # Skip the rest of the loop to re-init

            # The machine delegates updates and rendering to the active state.
            self.machine.handle_events(raw_events)
            self.machine.update(signals)
            self.machine.render(self.screen)

            pygame.display.flip()
            self.clock.tick(config.FPS)

        pygame.quit()

    def end_game(self):
        """Flags the game to exit the main loop."""
        self.running = False

    def restart_game(self):
        """Resets the game to its initial state."""
        # This is a simple (but effective) way to restart.
        # A more robust implementation might involve serializing/deserializing
        # the player and meta state to avoid a full re-initialization.
        self.__init__()
