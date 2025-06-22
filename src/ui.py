import pygame
import config
from collections import Counter


def render_inventory(screen, inventory, pos=(10, 10)):
    """Draws each item name × qty."""
    y_offset = 0
    item_counts = Counter(item.name for item in inventory)
    for item_name, qty in item_counts.items():
        text = f"{item_name} x{qty}"
        display_text(screen, text, (pos[0], pos[1] + y_offset), font_size=config.SMALL_FONT_SIZE)
        y_offset += 20

_last_message: str = ""

def notify(text: str):
    """
    Store and print a short player-facing message.
    """
    global _last_message
    _last_message = text
    print(text)

def get_last_message() -> str:
    """Return the most recently stored notify message."""
    return _last_message

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
    display_text(screen, label, (x, y - config.HEALTH_BAR_LABEL_Y_OFFSET), font_size=config.LARGE_FONT_SIZE, color=color)
    display_text(screen, f"{current} / {max_health}", (x + bar_width + config.HEALTH_BAR_TEXT_X_OFFSET, y), font_size=config.MEDIUM_FONT_SIZE, color=config.TEXT_COLOR)

def render_battle_screen(screen, battle_state):
    """Renders all elements of the battle screen."""
    screen.fill(config.BG_COLOR)  # Dark blue background

    render_inventory(screen, battle_state.player.inventory, pos=(10,10))

    # Draw health bars
    draw_health_bar(screen, *config.BATTLE_PLAYER_HEALTH_POS, battle_state.player.health, battle_state.player_max_health, config.PLAYER_HEALTH_COLOR, "Player")
    draw_health_bar(screen, *config.BATTLE_ENEMY_HEALTH_POS, battle_state.enemy.health, battle_state.enemy_max_health, config.ENEMY_HEALTH_COLOR, battle_state.enemy.name)

    # Score and wave
    display_text(screen, f"Score: {battle_state.score}", config.BATTLE_SCORE_POS, font_size=config.LARGE_FONT_SIZE, color=config.TEXT_COLOR)
    display_text(screen, f"Wave: {battle_state.wave+1}", config.BATTLE_WAVE_POS, font_size=config.MEDIUM_FONT_SIZE, color=config.TEXT_COLOR)

    # Instructions
    if battle_state.player_turn:
        display_text(screen, "SPACE: Attack    P: Potion    D: Defend    F: Flee", config.BATTLE_INSTRUCTIONS_POS, font_size=config.MEDIUM_FONT_SIZE, color=config.UI_ACCENT_COLOR)
    else:
        display_text(screen, "Enemy's turn...", config.BATTLE_INSTRUCTIONS_POS, font_size=config.MEDIUM_FONT_SIZE, color=config.ENEMY_TURN_COLOR)


    # Battle log (last 5 actions, fading)
    for i, msg in enumerate(reversed(battle_state.battle_log)):
        log_y = config.BATTLE_LOG_START_POS[1] + (i * config.BATTLE_LOG_LINE_SPACING)
        display_text(screen, msg, (config.BATTLE_LOG_START_POS[0], log_y), font_size=config.MEDIUM_FONT_SIZE, color=config.LOG_COLORS[i])
