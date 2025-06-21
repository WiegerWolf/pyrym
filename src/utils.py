import pygame

def load_image(file_path):
    """Load an image from the specified file path."""
    image = pygame.image.load(file_path)
    return image

def display_text(screen, text, position, font_size=30, color=(255, 255, 255)):
    """Display text on the screen at the specified position."""
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

def manage_game_settings(settings):
    """Manage game settings such as volume, difficulty, etc."""
    # Placeholder for managing game settings
    pass

def draw_health_bar(screen, x, y, current, max_health, color, label):
    bar_width = 200
    bar_height = 30
    fill = int(bar_width * (current / max_health))
    outline_rect = pygame.Rect(x, y, bar_width, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(screen, color, fill_rect)
    pygame.draw.rect(screen, (255,255,255), outline_rect, 2)
    display_text(screen, label, (x, y - 28), font_size=32, color=color)
    display_text(screen, f"{current} / {max_health}", (x + bar_width + 10, y), font_size=28, color=(255,255,255))

def add_to_log(battle_log, message, max_log=5):
    battle_log.append(message)
    if len(battle_log) > max_log:
        battle_log.pop(0)