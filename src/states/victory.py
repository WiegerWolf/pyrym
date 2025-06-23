# pylint: disable=no-member
"""victory.py: Displays victory screen and transitions to the shop."""
import pygame

from src import config
from src.core.ui import UI


class VictoryState:
    """Represents the state of the game after a victorious battle."""

    def __init__(self, _screen, player, meta, last_battle_log):
        """
        Initializes the victory state.

        Args:
            _screen: The screen surface (unused).
            player: The player character.
            meta: The encounter metadata.
            last_battle_log: The log from the last battle.
        """
        self.player = player
        self.meta = meta
        self.last_battle_log = last_battle_log

    def handle_events(self, events):
        """
        Handles events in the victory state.

        Args:
            events: A list of pygame events.

        Returns:
            A string indicating the next state, or None.
        """
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return "TO_SHOP"
        return None

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
