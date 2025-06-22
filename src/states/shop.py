"""
shop.py
Implements the shop where the player can buy items and upgrades.
"""
from collections import OrderedDict

import pygame

from src import config
from src.core.ui import UI
from src.core.game_state import StateManager
from src.items.items import HealingSalve, StaminaPotion


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
            "name": "Healing Salve", "cost": config.HEALING_SALVE_COST,
            "effect": self._buy_healing_salve, "desc": f"Heals {config.HEALING_SALVE_HEAL_AMOUNT} HP."
        }
        inventory['2'] = {
            "name": "Stamina Potion", "cost": config.STAMINA_POTION_COST,
            "effect": self._buy_stamina_potion, "desc": f"Grants +{config.STAMINA_POTION_STAMINA_GAIN} stamina."
        }
        inventory['3'] = {
            "name": "Power-Strike Upgrade", "cost": config.POWER_STRIKE_UPGRADE_COST,
            "effect": self._buy_power_strike_upgrade, "desc": f"Permanently +{config.POWER_STRIKE_UPGRADE_AMOUNT} dmg to Power Strike."
        }
        inventory['4'] = {
            "name": "Max-HP Blessing", "cost": config.MAX_HP_BLESSING_COST,
            "effect": self._buy_max_hp_blessing, "desc": f"+{config.MAX_HP_BLESSING_AMOUNT} max HP (one-time)."
        }
        return inventory
    
    def _buy_healing_salve(self):
        self.player.heal(config.HEALING_SALVE_HEAL_AMOUNT)
        self._show_purchase_message("Purchased Healing Salve!")

    def _buy_stamina_potion(self):
        self.player.gain_stamina(config.STAMINA_POTION_STAMINA_GAIN)
        self._show_purchase_message("Purchased Stamina Potion!")

    def _buy_power_strike_upgrade(self):
        self.player.power_strike_bonus += config.POWER_STRIKE_UPGRADE_AMOUNT
        self._show_purchase_message("Power-Strike Upgraded!")

    def _buy_max_hp_blessing(self):
        self.player.max_health += config.MAX_HP_BLESSING_AMOUNT
        self.player.heal(self.player.max_health) # Heal to full
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
        if signals.get("cheat_gold") and config.DEBUG:
            StateManager.adjust_gold(100)
        
        if signals.get("number_keys"):
            key_pressed = signals["number_keys"][0]
            if pygame.K_1 <= key_pressed <= pygame.K_4:
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

        if StateManager.gold >= item["cost"]:
            StateManager.adjust_gold(-item["cost"])
            item["effect"]()
        else:
            self._show_purchase_message("Not enough gold!")

    def render(self):
        self.screen.fill(config.BG_COLOR)
        
        # Title
        UI.display_text(self.screen, "Shop", config.SHOP_TITLE_POS, font_size=config.LARGE_FONT_SIZE)

        # Gold
        UI.display_text(self.screen, f"Gold: {StateManager.gold} g", config.SHOP_GOLD_POS)

        # Items
        y_offset = 0
        for key, item in self.items.items():
            is_disabled = False
            is_one_time_purchased = (item["name"] == "Max-HP Blessing" and 
                                     StateManager.purchased_flags.get("max_hp_blessing"))

            if is_one_time_purchased:
                is_disabled = True
            
            color = config.TEXT_COLOR
            if StateManager.gold < item['cost'] or is_disabled:
                color = (150, 150, 150) # Greyed out

            text = f"{key}) {item['name']} - {item['cost']} g"
            if is_disabled:
                text += " (Purchased)"

            UI.display_text(
                self.screen, text,
                (config.SHOP_MENU_START_X, config.SHOP_MENU_START_Y + y_offset),
                color=color
            )
            y_offset += config.SHOP_LINE_SPACING

        # Exit
        UI.display_text(self.screen, "Q) Exit Shop", (config.SHOP_MENU_START_X, config.SHOP_MENU_START_Y + y_offset + 20))

        # Purchase Message
        if self.purchase_message:
            UI.display_text(self.screen, self.purchase_message, (350, 500), color=(255, 255, 0))