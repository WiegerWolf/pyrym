import pygame
from src.core.ui import UI
from src import config


class VictoryState:
    def __init__(self, screen, player, meta, last_battle_log):
        self.player = player
        self.meta = meta
        self.last_battle_log = last_battle_log

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return "TO_SHOP"
        return None

    def render(self, screen):
        screen.fill((0, 0, 0))
        y_offset = 50
        for msg in self.last_battle_log:
            UI.display_text(screen, msg, (50, y_offset))
            y_offset += 30
        UI.display_text(
            screen,
            "Press SPACE to continue",
            (screen.get_width() // 2 - 150, screen.get_height() - 100),
            font_size=config.DEFAULT_FONT_SIZE
        )