# pylint: disable=no-member
"""victory.py: Displays victory screen and transitions to the shop."""
import pygame

from src import config
from src.core.state_machine import BaseState
from src.core.ui import UI
from .shop import ShopState


class VictoryState(BaseState):
    """Represents the state of the game after a victorious battle."""

    def __init__(self, player, meta, screen, last_battle_log):
        """
        Initializes the victory state.

        Args:
            player: The player character.
            meta: The encounter metadata.
            screen: The screen surface to draw on.
            last_battle_log: The log from the last battle.
        """
        super().__init__()
        self.player = player
        self.meta = meta
        self.screen = screen
        self.last_battle_log = last_battle_log

    def handle_events(self, events):
        """
        Handles events in the victory state.
        """
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.machine.change(ShopState(self.player, self.meta, self.screen))

    def render(self, screen):
        """
        Renders the victory screen.

        Args:
            screen: The screen surface to draw on.
        """
        screen.fill((0, 0, 0))
        y_offset = 50
        for msg in self.last_battle_log:
            UI.display_text(screen, msg, (50, y_offset))
            y_offset += 30
        UI.display_text(
            screen,
            "Press SPACE to continue",
            (screen.get_width() // 2 - 150, screen.get_height() - 100),
            font_size=config.DEFAULT_FONT_SIZE,
        )
