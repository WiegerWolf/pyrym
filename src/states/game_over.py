# pylint: disable=no-member
"""game_over.py: Displays the game over screen and handles restart/quit."""
import pygame

from src import config
from src.core.ui import UI


class GameOverState:
    """Represents the state when the game is over."""

    def __init__(self, _screen, player, meta, last_battle_log=None):
        """
        Initializes the game over state.
        Args:
            _screen: The screen surface (unused).
            player: The player character.
            meta: The encounter metadata.
            last_battle_log: The log from the last battle.
        """
        self.player = player
        self.meta = meta
        self.battle_log = last_battle_log or []

    def handle_events(self, events):
        """
        Handles events in the game over state.

        Args:
            events: A list of pygame events.

        Returns:
            A string indicating the next state, or None.
        """
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "RESTART"
                if event.key == pygame.K_q:
                    return "QUIT"
        return None

    def render(self, screen):
        """
        Renders the game over screen.

        Args:
            screen: The screen surface to draw on.
        """
        screen.fill((0, 0, 0))
        UI.display_text(
            screen, "GAME OVER", (screen.get_width()//2 - 100, 50),
            font_size=config.LARGE_FONT_SIZE, color=(255, 0, 0)
        )
        stats_y = 120
        for text in [
            f"Total Turns: {self.meta.turns}",
            f"Battles Won: {self.meta.battles_won}",
            f"Final Gold: {self.player.gold}"
        ]:
            UI.display_text(screen, text, (screen.get_width()//2 - 100, stats_y))
            stats_y += 40

        # Render battle log
        log_y = stats_y + 20
        for msg in self.battle_log:
            UI.display_text(screen, msg, (50, log_y))
            log_y += 30

        UI.display_text(
            screen, "Press Q to quit, R to restart",
            (screen.get_width()//2 - 120, screen.get_height() - 100)
        )
