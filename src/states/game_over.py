import pygame
import pygame
from src.core.ui import UI
from src import config


class GameOverState:
    def __init__(self, screen, player, meta, last_battle_log=None):
        self.player = player
        self.meta = meta
        self.battle_log = last_battle_log or []

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "RESTART"
                if event.key == pygame.K_q:
                    return "QUIT"
        return None

    def render(self, screen):
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