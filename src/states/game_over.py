import pygame
from src.states.base import State
from src.core.ui import font

class GameOverState(State):
    def __init__(self, player, meta):
        super().__init__()
        self.player = player
        self.meta = meta

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "RESTART"
        return None

    def render(self, screen):
        screen.fill((0, 0, 0))
        
        title_surface = font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(title_surface, (screen.get_width() // 2 - title_surface.get_width() // 2, 100))
        
        stats_y_offset = 200
        stats = [
            f"Total Turns: {self.meta.turns}",
            f"Battles Won: {self.meta.battles_won}",
            f"Final Gold: {self.player.gold}"
        ]
        
        for stat in stats:
            stat_surface = font.render(stat, True, (255, 255, 255))
            screen.blit(stat_surface, (screen.get_width() // 2 - stat_surface.get_width() // 2, stats_y_offset))
            stats_y_offset += 40
            
        restart_surface = font.render("Press R to restart", True, (255, 255, 255))
        screen.blit(restart_surface, (screen.get_width() // 2 - restart_surface.get_width() // 2, screen.get_height() - 100))