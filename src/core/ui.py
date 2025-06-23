"""
ui.py
Handles all UI rendering for the game.
"""
from collections import Counter

import pygame

from src import config
from src.core.game_state import StateManager
from ..utils import HealthBarSpec


class UI:
    """
    UI contains all rendering functions for the game.
    This class wraps original functions as static methods to fix import errors.
    """

    _last_message: str = ""

    @staticmethod
    def render_inventory(screen, inventory, pos=(10, 10)):
        """Draws each item name × qty."""
        y_offset = 0
        item_counts = Counter(item.name for item in inventory)
        for item_name, qty in item_counts.items():
            text = f"{item_name} x{qty}"
            UI.display_text(
                screen, text, (pos[0], pos[1] + y_offset), font_size=config.SMALL_FONT_SIZE
            )
            y_offset += 20

    @classmethod
    def notify(cls, text: str):
        """
        Store and print a short player-facing message.
        """
        cls._last_message = text
        print(text)

    @classmethod
    def get_last_message(cls) -> str:
        """Return the most recently stored notify message."""
        return cls._last_message

    @staticmethod
    def display_text(
        screen, text, position,
        font_size=config.DEFAULT_FONT_SIZE,
        color=config.TEXT_COLOR
    ):
        """Display text on the screen at the specified position."""
        font = pygame.font.Font(None, font_size)
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, position)

    @staticmethod
    def draw_health_bar(screen, spec: HealthBarSpec):
        """Draws a health bar using a HealthBarSpec."""
        bar_width = config.HEALTH_BAR_WIDTH
        bar_height = config.HEALTH_BAR_HEIGHT

        # Prevent division by zero if max_val is 0
        fill_ratio = spec.current / spec.max_val if spec.max_val > 0 else 0
        fill = int(bar_width * fill_ratio)

        outline_rect = pygame.Rect(spec.x, spec.y, bar_width, bar_height)
        fill_rect = pygame.Rect(spec.x, spec.y, fill, bar_height)

        pygame.draw.rect(screen, spec.color, fill_rect)
        pygame.draw.rect(screen, config.TEXT_COLOR, outline_rect, 2)

        UI.display_text(
            screen,
            spec.label,
            (spec.x, spec.y - config.HEALTH_BAR_LABEL_Y_OFFSET),
            font_size=config.LARGE_FONT_SIZE,
            color=spec.color,
        )
        UI.display_text(
            screen,
            f"{spec.current} / {spec.max_val}",
            (spec.x + bar_width + config.HEALTH_BAR_TEXT_X_OFFSET, spec.y),
            font_size=config.MEDIUM_FONT_SIZE,
            color=config.TEXT_COLOR,
        )

    @staticmethod
    def render_battle_screen(screen, battle_state):
        """Renders all elements of the battle screen."""
        screen.fill(config.BG_COLOR)

        UI.render_inventory(screen, battle_state.player.inventory, pos=(10, 10))

        # Health bars
        player_health_spec = HealthBarSpec(
            *config.BATTLE_PLAYER_HEALTH_POS,
            current=battle_state.player.health,
            max_val=battle_state.player_max_health,
            color=config.PLAYER_HEALTH_COLOR,
            label="Player",
        )
        enemy_health_spec = HealthBarSpec(
            *config.BATTLE_ENEMY_HEALTH_POS,
            current=battle_state.enemy.health,
            max_val=battle_state.enemy_max_health,
            color=config.ENEMY_HEALTH_COLOR,
            label=battle_state.enemy.name,
        )
        UI.draw_health_bar(screen, player_health_spec)
        UI.draw_health_bar(screen, enemy_health_spec)

        # Stamina
        stamina_text = (
            f"STA: {battle_state.player.stamina}/"
            f"{battle_state.player.max_stamina}"
        )
        UI.display_text(screen, stamina_text,
                        (config.BATTLE_PLAYER_HEALTH_POS[0],
                         config.BATTLE_PLAYER_HEALTH_POS[1] + 40))


        # Score and wave
        UI.display_text(
            screen,
            f"Score: {battle_state.meta.score}",
            config.BATTLE_SCORE_POS,
            font_size=config.LARGE_FONT_SIZE,
        )
        UI.display_text(
            screen,
            f"Wave: {battle_state.meta.wave + 1}",
            config.BATTLE_WAVE_POS,
            font_size=config.MEDIUM_FONT_SIZE,
        )

        # Gold display
        UI.display_text(
            screen,
            f"Gold: {StateManager.gold}",
            config.BATTLE_GOLD_POS,
            font_size=config.LARGE_FONT_SIZE,
            color=config.TEXT_COLOR
        )

        # Instructions
        if battle_state.player_turn:
            if battle_state.item_menu_open:
                UI.display_text(
                    screen,
                    "Select an item (1-9) or (I) to cancel",
                    config.BATTLE_INSTRUCTIONS_POS,
                    font_size=config.MEDIUM_FONT_SIZE,
                    color=config.UI_ACCENT_COLOR,
                )
            else:
                actions = ["(A)ttack", "(D)efend"]
                if battle_state.player.inventory:
                    actions.append("(I)tem")
                actions.append("(F)lee")
                UI.display_text(
                    screen,
                    "    ".join(actions),
                    config.BATTLE_INSTRUCTIONS_POS,
                    font_size=config.MEDIUM_FONT_SIZE,
                    color=config.UI_ACCENT_COLOR,
                )
        else:
            UI.display_text(
                screen,
                "Enemy's turn...",
                config.BATTLE_INSTRUCTIONS_POS,
                font_size=config.MEDIUM_FONT_SIZE,
                color=config.ENEMY_TURN_COLOR,
            )


        # Battle log (last 5 actions, fading)
        # Battle log (last 5 actions, fading)
        for i, msg in enumerate(reversed(battle_state.battle_log)):
            log_y = (config.BATTLE_LOG_START_POS[1] +
                     (i * config.BATTLE_LOG_LINE_SPACING))
            UI.display_text(
                screen,
                msg,
                (config.BATTLE_LOG_START_POS[0], log_y),
                font_size=config.MEDIUM_FONT_SIZE,
                color=config.LOG_COLORS[i],
            )

def render_battle_screen(*args, **kwargs):
    """
    Back-compat shim. Delegates to UI().render_battle_screen()
    so legacy code importing this free function continues to work
    until everything is refactored.
    """
    return UI().render_battle_screen(*args, **kwargs)
