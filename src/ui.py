import pygame
import config

def display_text(screen, text, position, font_size=config.DEFAULT_FONT_SIZE, color=config.TEXT_COLOR):
    """Display text on the screen at the specified position."""
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

def draw_health_bar(screen, x, y, current, max_health, color, label):
    bar_width = config.HEALTH_BAR_WIDTH
    bar_height = config.HEALTH_BAR_HEIGHT
    fill = int(bar_width * (current / max_health))
    outline_rect = pygame.Rect(x, y, bar_width, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(screen, color, fill_rect)
    pygame.draw.rect(screen, config.TEXT_COLOR, outline_rect, 2)
    display_text(screen, label, (x, y - 28), font_size=config.LARGE_FONT_SIZE, color=color)
    display_text(screen, f"{current} / {max_health}", (x + bar_width + 10, y), font_size=config.MEDIUM_FONT_SIZE, color=config.TEXT_COLOR)
