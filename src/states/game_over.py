# pylint: disable=no-member
"""game_over.py: Displays the game over screen and handles restart/quit."""
import pygame

from src import config
from src.core.state_machine import BaseState
from src.core.ui import UI


class GameOverState(BaseState):
    """Represents the state when the game is over."""

    def __init__(self, player, meta, screen, last_battle_log=None):
        """
        Initializes the game over state.
        Args:
            player: The player character.
            meta: The encounter metadata.
            screen: The screen to render to.
            last_battle_log: The log from the last battle.
        """
        super().__init__()
        self.player = player
        self.meta = meta
        self.screen = screen
        self.battle_log = last_battle_log or []

    def handle_events(self, events):
        """
        Handles events in the game over state.
        """
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # The `game` object is not directly available, but we can signal a restart.
                    # The main game loop will catch this and call the restart method.
                    self.machine.game.restart_game()
                if event.key == pygame.K_q:
                    self.machine.game.end_game()

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
