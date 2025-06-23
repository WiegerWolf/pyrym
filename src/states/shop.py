"""
shop.py
Implements the shop where the player can buy items and upgrades.
"""
from collections import OrderedDict

import pygame

from src import config
from src.core.state_machine import BaseState
from src.core.ui import UI
from src.items.items import HealingPotion, StaminaPotion
from src.utils import scaled_cost


class ShopState(BaseState):
    """
    Manages the shop state, allowing the player to purchase items and upgrades.
    """

    def __init__(self, player, meta, screen):
        super().__init__()
        self.player = player
        self.meta = meta
        self.screen = screen
        self.purchase_message = ""
        self.message_timer = 0
        self.items = OrderedDict()
        self._build_inventory()

    def enter(self, prev_state, **kwargs):
        """Display a welcome message when entering the shop."""
        self.purchase_message = "Welcome to the shop!"
        self.message_timer = pygame.time.get_ticks()
        self._build_inventory() # Rebuild to reflect player's current stats

    def _build_inventory(self):
        """Dynamically builds the shop's inventory list."""
        self.items.clear()
        self.items['1'] = {
            "name": "Healing Potion", "cost": config.HEALING_POTION_COST,
            "effect": self._buy_healing_potion, "price_type": "gold",
            "desc": f"Heals {config.HEALING_POTION_HEAL_AMOUNT} HP."
        }
        self.items['2'] = {
            "name": "Stamina Potion", "cost": config.STAMINA_POTION_COST,
            "effect": self._buy_stamina_potion, "price_type": "gold",
            "desc": f"Grants +{config.STAMINA_POTION_STAMINA_GAIN} stamina."
        }

        # Damage Boost
        dmg_level = self.player.state.damage_boost_lvl
        dmg_cost = scaled_cost(config.DAMAGE_BOOST_BASE_COST, dmg_level, config.BOOST_COST_GROWTH)
        self.items['3'] = {
            "name": "Damage Boost",
            "cost": dmg_cost, "price_type": "xp",
            "effect": self._buy_damage_boost,
            "desc": f"Lvl {dmg_level + 1}: +{config.DAMAGE_BOOST_PCT:.0%} total damage."
        }

        # HP Boost
        hp_level = self.player.state.hp_boost_lvl
        hp_cost = scaled_cost(config.HP_BOOST_BASE_COST, hp_level, config.BOOST_COST_GROWTH)
        self.items['4'] = {
            "name": "Max-HP Boost",
            "cost": hp_cost, "price_type": "xp",
            "effect": self._buy_max_hp_boost,
            "desc": f"Lvl {hp_level + 1}: +{config.MAX_HP_BOOST_PCT:.0%} max HP & full heal."
        }

    def _buy_healing_potion(self):
        """Buy a healing potion."""
        self.player.add_item(HealingPotion())
        self._show_purchase_message("Purchased Healing Potion!")

    def _buy_stamina_potion(self):
        """Buy a stamina potion."""
        self.player.add_item(StaminaPotion())
        self._show_purchase_message("Purchased Stamina Potion!")

    def _buy_damage_boost(self):
        """Buy a damage boost upgrade."""
        self.player.state.damage_boost_lvl += 1
        self.player.damage_mult += config.DAMAGE_BOOST_PCT
        self._show_purchase_message("Damage Boosted!")
        self._build_inventory() # Refresh costs and descriptions

    def _buy_max_hp_boost(self):
        """Buy a max HP boost upgrade."""
        self.player.state.hp_boost_lvl += 1
        self.player.max_hp_mult += config.MAX_HP_BOOST_PCT
        self.player.heal(self.player.max_health)  # Heal to full
        self._show_purchase_message("Max-HP Boosted!")
        self._build_inventory() # Refresh costs and descriptions

    def _show_purchase_message(self, message):
        """Displays a temporary purchase confirmation message."""
        self.purchase_message = message
        self.message_timer = pygame.time.get_ticks()

    def update(self, signals: dict) -> None:
        """Update shop logic based on input signals."""
        from .explore import ExploreState  # Lazy import

        if self.purchase_message and pygame.time.get_ticks() - self.message_timer > 1500:
            self.purchase_message = ""

        if signals.get("quit_shop"):
            self.machine.change(ExploreState(self.player, self.meta, self.screen))
            return

        if signals.get("number_keys"):
            key_pressed = signals["number_keys"][0]
            if pygame.K_1 <= key_pressed <= pygame.K_4:
                self.purchase_item(chr(key_pressed))

    def purchase_item(self, key: str):
        """Attempts to purchase an item based on the key pressed."""
        item = self.items.get(key)
        if not item:
            return

        price_type = item.get("price_type", "gold")
        if price_type == "xp":
            if self.player.spend_xp(item["cost"]):
                item["effect"]()
                self._show_purchase_message("Purchase successful!")
            else:
                self._show_purchase_message("Not enough XP!")
        else:
            if self.player.spend_gold(item["cost"]):
                item["effect"]()
            else:
                self._show_purchase_message("Not enough gold!")

    def render(self, screen):
        """Renders the shop screen."""
        screen.fill(config.BG_COLOR)

        # Title
        UI.display_text(screen, "Shop", config.SHOP_TITLE_POS,
                        font_size=config.LARGE_FONT_SIZE)

        self._render_player_stats(screen)

        # Items
        y_offset = 0
        for key, item in self.items.items():
            color = config.TEXT_COLOR
            currency_suffix = "XP" if item.get("price_type") == "xp" else "G"

            can_afford = False
            if item.get("price_type") == "xp":
                can_afford = self.player.xp >= item['cost']
            else:
                can_afford = self.player.gold >= item['cost']

            if not can_afford:
                color = (150, 150, 150)  # Greyed out

            text = f"{key}) {item['name']} - {item['cost']} {currency_suffix}"

            UI.display_text(
                screen, text,
                (config.SHOP_MENU_START_X, config.SHOP_MENU_START_Y + y_offset),
                color=color
            )

            desc_color = color if color != config.TEXT_COLOR else config.UI_ACCENT_COLOR
            UI.display_text(
                screen,
                f"   {item['desc']}",
                (config.SHOP_MENU_START_X + 20,
                 config.SHOP_MENU_START_Y + y_offset + 20),
                font_size=config.SMALL_FONT_SIZE,
                color=desc_color
            )
            y_offset += config.SHOP_LINE_SPACING + 20

        # Exit
        UI.display_text(screen, "Q) Exit Shop",
                        (config.SHOP_MENU_START_X,
                         config.SHOP_MENU_START_Y + y_offset + 20))

        # Purchase Message
        if self.purchase_message:
            UI.display_text(
                screen, self.purchase_message, (350, 500), color=(255, 255, 0)
            )


    def _render_player_stats(self, screen):
        """Renders the player's current stats (HP, Gold, XP) and inventory."""
        stats_line_1 = (f"HP  {self.player.health} / {self.player.max_health}    "
                        f"Gold  {self.player.gold} G    "
                        f"XP  {self.player.xp}")
        UI.display_text(screen, stats_line_1, (10, 10))

        # Render inventory below the stats
        UI.render_inventory(screen, self.player.inventory, pos=(10, 40))
