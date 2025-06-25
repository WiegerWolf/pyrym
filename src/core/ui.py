"""
ui.py
Handles all UI rendering for the game.

Includes helpers for transient messages and status icons.
"""
import pygame

from src import config
from ..utils import HealthBarSpec, group_inventory


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
        grouped_items = group_inventory(inventory)
        for idx, (item, qty, _) in enumerate(grouped_items[:9]):
            text = f"{idx + 1}. {item.name} x{qty}"
            UI.display_text(
                screen, text, (pos[0], pos[1] + y_offset), font_size=config.SMALL_FONT_SIZE
            )
            y_offset += 20
            desc_text = f"  {item.description}"
            UI.display_text(
                screen, desc_text, (pos[0], pos[1] + y_offset),
                font_size=config.SMALL_FONT_SIZE - 4, color=config.UI_ACCENT_COLOR
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
    def display_text(  # pylint: disable=too-many-arguments
        screen,
        text,
        position,
        font_size=config.DEFAULT_FONT_SIZE,
        color=config.TEXT_COLOR,
        center: bool = False,
    ):
        """
        Display text on the screen at the specified position.

        If `center` is True, `position` is treated as the center coordinate.
        """
        font = pygame.font.Font(None, font_size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = position
        else:
            text_rect.topleft = position
        screen.blit(text_surface, text_rect)

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
    def format_skill_label(skill, keybind: str, remaining_cd: int) -> str:
        """Formats a skill's name and cooldown status for the UI."""
        name = skill.name
        if remaining_cd > 0:
            return f"{keybind} {name} ({remaining_cd})"
        return f"{keybind} {name} READY"

    @staticmethod
    def render_skill_bar(screen, skills: list, cooldowns: dict, font, x: int, y: int):
        """
        Render skill hot-key labels and remaining cool-downs.

        Example output:
        Q Shield Bash (2)   W Adrenaline Rush READY   E--   R--
        Grey out text when CD > 0.
        """
        keys = ["Q", "W", "E", "R"]
        offset = 0
        for i, key in enumerate(keys):
            if i < len(skills):
                skill = skills[i]
                cd = cooldowns.get(skill.name, 0)
                label = UI.format_skill_label(skill, key, cd)
                color = (150, 150, 150) if cd > 0 else config.TEXT_COLOR
            else:
                label = f"{key}--"
                color = config.TEXT_COLOR

            text_surface = font.render(label, True, color)
            screen.blit(text_surface, (x + offset, y))
            offset += text_surface.get_width() + 10

    @staticmethod
    def render_battle_screen(screen, battle_state):
        """Renders all elements of the battle screen."""
        screen.fill(config.BG_COLOR)

        inventory_pos = (config.SCREEN_WIDTH - 250, config.SCREEN_HEIGHT - 210)
        UI.render_inventory(screen, battle_state.player.inventory, pos=inventory_pos)

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

        # Skill bar
        y_offset = config.BATTLE_PLAYER_HEALTH_POS[1] + 70
        small_font = pygame.font.Font(None, config.SMALL_FONT_SIZE)
        UI.render_skill_bar(screen, battle_state.player.skills,
                            battle_state.player.cooldowns, small_font, 20,
                            y_offset)


        # Score

        # Gold display
        UI.display_text(
            screen,
            f"Gold: {battle_state.player.gold}",
            config.BATTLE_GOLD_POS,
            font_size=config.LARGE_FONT_SIZE,
            color=config.TEXT_COLOR
        )

        # Instructions
        if battle_state.player_turn:
            actions = ["(A)ttack", "(D)efend", "(F)lee"]
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

    @staticmethod
    def render_explore_log(screen, log):
        """Renders the exploration log."""
        for i, msg in enumerate(reversed(log[-5:])):
            log_y = (config.BATTLE_LOG_START_POS[1] +
                     (i * config.BATTLE_LOG_LINE_SPACING))
            UI.display_text(
                screen,
                msg,
                (config.BATTLE_LOG_START_POS[0], log_y),
                font_size=config.MEDIUM_FONT_SIZE,
                color=config.LOG_COLORS[i],
            )


def flash_message(screen: pygame.Surface, text: str,
                    duration: int = 40,  # pylint: disable=unused-argument
                    pos: tuple[int, int] | None = None,
                    color: tuple[int, int, int] = config.TEXT_COLOR) -> None:
    """
    Draws `text` centered (or at `pos`) for `duration` frames.
    Caller must call this every frame until duration elapses.
    This is a simple utility; no timing manager is added here.
    """
    if pos is None:
        pos = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
    UI.display_text(screen, text, pos, font_size=config.LARGE_FONT_SIZE, color=color, center=True)


def render_status_icons(surface: pygame.Surface, entity, pos: tuple[int, int]) -> None:
    """
    Draw a 16×16 coloured square and a text label for each active status.
    pos = (x, y) top-left anchor; icons and labels stack horizontally.
    Uses entity.statuses; colour mapping hard-coded for now.
    """
    colour_map = {
        "poison": (80, 200, 120),
        "bleed": (200, 40, 40),
        "stun": (255, 215, 0),
        "regeneration": (50, 180, 255),
    }
    icon_size = 16
    padding = 4  # Increased padding for text
    base_x, base_y = pos
    current_x = base_x

    for status in entity.statuses:
        # Draw the icon
        colour = colour_map.get(status.name.lower(), (150, 150, 150))
        rect = pygame.Rect(current_x, base_y, icon_size, icon_size)
        pygame.draw.rect(surface, colour, rect)
        current_x += icon_size + padding

        # Draw the text label
        label = f"{status.name.capitalize()} ({status.duration})"
        UI.display_text(
            surface,
            label,
            (current_x, base_y),
            font_size=config.SMALL_FONT_SIZE - 2,
            color=colour
        )
        
        # Advance current_x by the width of the text plus padding
        font = pygame.font.Font(None, config.SMALL_FONT_SIZE - 2)
        text_width, _ = font.size(label)
        current_x += text_width + padding * 3

def render_battle_screen(*args, **kwargs):
    """
    Back-compat shim. Delegates to UI().render_battle_screen()
    so legacy code importing this free function continues to work
    until everything is refactored.
    """
    return UI().render_battle_screen(*args, **kwargs)
