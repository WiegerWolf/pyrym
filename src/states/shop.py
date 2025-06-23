"""
shop.py
Implements the shop where the player can buy items and upgrades.
"""
from collections import OrderedDict

import pygame

from src import config
from src.core.ui import UI
from src.core.game_state import StateManager
from src.items.items import HealingPotion


class ShopState:
    """
    Manages the shop state, allowing the player to purchase items and upgrades.
    """

    def __init__(self, screen, player):
        self.screen = screen
        self.player = player
        self.font = pygame.font.Font(None, config.LARGE_FONT_SIZE)
        self.purchase_message = ""
        self.message_timer = 0
        self.items = self._build_inventory()

    def _build_inventory(self) -> OrderedDict:
        """Builds the shop's inventory list."""
        inventory = OrderedDict()
        inventory['1'] = {
            "name": "Healing Potion", "cost": config.HEALING_POTION_COST,
            "effect": self._buy_healing_potion, "price_type": "gold",
            "desc": f"Heals {config.HEALING_POTION_HEAL_AMOUNT} HP."
        }
        inventory['2'] = {
            "name": "Stamina Potion", "cost": config.STAMINA_POTION_COST,
            "effect": self._buy_stamina_potion, "price_type": "gold",
            "desc": f"Grants +{config.STAMINA_POTION_STAMINA_GAIN} stamina."
        }
        inventory['3'] = {
            "name": "Damage Upgrade",
            "cost": config.POWER_STRIKE_UPGRADE_COST, "price_type": "xp",
            "effect": self._buy_power_strike_upgrade,
            "desc": f"Permanently +{config.POWER_STRIKE_UPGRADE_AMOUNT} "
                    "base damage to ALL attacks."
        }
        inventory['4'] = {
            "name": "Max-HP Blessing",
            "cost": config.MAX_HP_BLESSING_COST, "price_type": "xp",
            "effect": self._buy_max_hp_blessing,
            "desc": f"+{config.MAX_HP_BLESSING_AMOUNT} max HP (one-time)."
        }
        return inventory

    def _buy_healing_potion(self):
        """Buy a healing potion."""
        self.player.add_item(HealingPotion())
        self._show_purchase_message("Purchased Healing Potion!")

    def _buy_stamina_potion(self):
        """Buy a stamina potion."""
        self.player.gain_stamina(config.STAMINA_POTION_STAMINA_GAIN)
        self._show_purchase_message("Purchased Stamina Potion!")

    def _buy_power_strike_upgrade(self):
        """Buy a power strike upgrade."""
        self.player.state.power_strike_bonus += config.POWER_STRIKE_UPGRADE_AMOUNT
        self._show_purchase_message("Damage Upgraded!")

    def _buy_max_hp_blessing(self):
        """Buy a max HP blessing."""
        self.player.max_health += config.MAX_HP_BLESSING_AMOUNT
        self.player.heal(self.player.max_health)  # Heal to full
        StateManager.purchased_flags['max_hp_blessing'] = True
        self._show_purchase_message("Max-HP Increased!")

    def _show_purchase_message(self, message):
        """Displays a temporary purchase confirmation message."""
        self.purchase_message = message
        self.message_timer = pygame.time.get_ticks()

    def update(self, signals):
        """
        Update shop logic based on input signals.
        Returns a dictionary indicating the next state, or None.
        """
        if self.purchase_message and pygame.time.get_ticks() - self.message_timer > 1000:
            self.purchase_message = ""

        if signals.get("quit_shop"):
            return {"next_state": "EXPLORE"}

        if signals.get("number_keys"):
            key_pressed = signals["number_keys"][0]
            key_1 = pygame.key.key_code("1")
            key_4 = pygame.key.key_code("4")
            if key_1 <= key_pressed <= key_4:
                self.purchase_item(chr(key_pressed))

        return None

    def purchase_item(self, key: str):
        """Attempts to purchase an item based on the key pressed."""
        item = self.items.get(key)
        if not item:
            return

        is_one_time = item["name"] == "Max-HP Blessing"
        if is_one_time and StateManager.purchased_flags.get("max_hp_blessing"):
            self._show_purchase_message("Already purchased!")
            return

        price_type = item.get("price_type", "gold")
        if price_type == "xp":
            if self.player.spend_xp(item["cost"]):
                item["effect"]()
                self._show_purchase_message("Purchase successful!")
            else:
                self._show_purchase_message("Not enough XP!")
        else:
            if StateManager.gold >= item["cost"]:
                StateManager.adjust_gold(-item["cost"])
                item["effect"]()
            else:
                self._show_purchase_message("Not enough gold!")

    def render(self):
        """Renders the shop screen."""
        self.screen.fill(config.BG_COLOR)

        # Title
        UI.display_text(self.screen, "Shop", config.SHOP_TITLE_POS,
                        font_size=config.LARGE_FONT_SIZE)

        self._render_player_stats()

        # Items
        y_offset = 0
        for key, item in self.items.items():
            is_one_time_purchased = (item["name"] == "Max-HP Blessing" and
                                     StateManager.purchased_flags.get("max_hp_blessing"))

            is_disabled = is_one_time_purchased

            color = config.TEXT_COLOR
            currency_suffix = "XP" if item.get("price_type") == "xp" else "G"
            
            can_afford = False
            if item.get("price_type") == "xp":
                can_afford = self.player.xp >= item['cost']
            else:
                can_afford = StateManager.gold >= item['cost']

            if not can_afford or is_disabled:
                color = (150, 150, 150)  # Greyed out
            
            text = f"{key}) {item['name']} - {item['cost']} {currency_suffix}"
            if is_disabled:
                text += " (Purchased)"

            UI.display_text(
                self.screen, text,
                (config.SHOP_MENU_START_X, config.SHOP_MENU_START_Y + y_offset),
                color=color
            )

            desc_color = color if color != config.TEXT_COLOR else config.UI_ACCENT_COLOR
            UI.display_text(
                self.screen,
                f"   {item['desc']}",
                (config.SHOP_MENU_START_X + 20,
                 config.SHOP_MENU_START_Y + y_offset + 20),
                font_size=config.SMALL_FONT_SIZE,
                color=desc_color
            )
            y_offset += config.SHOP_LINE_SPACING + 20

        # Exit
        UI.display_text(self.screen, "Q) Exit Shop",
                        (config.SHOP_MENU_START_X,
                         config.SHOP_MENU_START_Y + y_offset + 20))

        # Purchase Message
        if self.purchase_message:
            UI.display_text(
                self.screen, self.purchase_message, (350, 500), color=(255, 255, 0)
            )


    def _render_player_stats(self):
        """Renders the player's current stats (HP, Gold, XP) and inventory."""
        stats_line_1 = (f"HP  {self.player.health} / {self.player.max_health}    "
                        f"Gold  {StateManager.gold} G    "
                        f"XP  {self.player.xp}")
        UI.display_text(self.screen, stats_line_1, (10, 10))

        # Render inventory below the stats
        UI.render_inventory(self.screen, self.player.inventory, pos=(10, 40))


if __name__ == '__main__':
    # Unit-style test stub
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from src.entities.player import Player

    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    player = Player()
    player.gain_xp(230)
    player.health = 47
    player.max_health = 60
    player.add_item(HealingPotion())
    StateManager.gold = 125

    shop_state = ShopState(screen, player)
    shop_state.render()

    pygame.display.flip()  # Update the full display Surface to the screen
    pygame.time.wait(2000)
    pygame.quit()
    print("ShopState render test completed successfully.")

