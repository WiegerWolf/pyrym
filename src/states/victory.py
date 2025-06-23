import pygame
from src.states.base import State
from src.core.ui import font

class VictoryState(State):
    def __init__(self, player, meta, last_battle_log):
        super().__init__()
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
        for message in self.last_battle_log:
            text_surface = font.render(message, True, (255, 255, 255))
            screen.blit(text_surface, (50, y_offset))
            y_offset += 30
            
        text_surface = font.render("Press SPACE to continue", True, (255, 255, 255))
        screen.blit(text_surface, (screen.get_width() // 2 - text_surface.get_width() // 2, screen.get_height() - 100))