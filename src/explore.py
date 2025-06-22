import pygame
import config
from ui import display_text
from state import GameState, StateManager

class ExploreState:
    """A placeholder state for exploration."""

    def __init__(self, screen):
        self.screen = screen
        self.state_manager = StateManager()

    def update(self, signals):
        """Update exploration state. For now, it just checks for input."""
        if signals.get("return_battle"):
            # The main loop will handle the state change
            return False  # Signal to exit this state's loop
        return True

    def render(self):
        """Render the exploration screen."""
        self.screen.fill(config.BG_COLOR)
        text = "Exploration Mode – press B to return to battle"
        
        # Center the text
        font = pygame.font.Font(None, config.LARGE_FONT_SIZE)
        text_surface = font.render(text, True, config.TEXT_COLOR)
        text_rect = text_surface.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2))
        
        self.screen.blit(text_surface, text_rect)
        
    # The handle_input method is removed as this logic is now in GameManager.