"""
battle.py
Manages the state of a battle encounter.
"""
import random

from .. import config
from ..core.state_machine import BaseState
from ..core.ui import render_battle_screen, UI
from ..items.items import HealingPotion
from ..utils import add_to_log, EncounterMeta, handle_item_use


class BattleState(BaseState):
    """Manages the state of a single battle encounter."""

    def __init__(self, player, enemy, encounter_meta: EncounterMeta, screen):
        super().__init__()
        self.player = player
        self.enemy = enemy
        self.meta = encounter_meta
        self.screen = screen
        self.item_menu_open = False
        self.player_turn = True
        self.battle_log = []

    def enter(self, prev_state, **kwargs):
        """Reset entities and prepare for battle."""
        self.player.battle_reset()
        self.enemy.reset()
        add_to_log(self.battle_log, f"A wild {self.enemy.name} appears!")

    @property
    def player_max_health(self):
        """Returns the player's maximum health."""
        return self.player.max_health

    @property
    def enemy_max_health(self):
        """Returns the enemy's maximum health."""
        return self.enemy.max_health

    def player_action(self, action='attack'):
        """
        Executes a player action (attack, heal, or defend).
        Returns the action message for logging.
        """
        msg = ""  # Default message if no action is taken
        if self.player_turn:
            if action == 'attack':
                result = self.player.attack_action(self.enemy)
                if result.get("no_stamina"):
                    add_to_log(self.battle_log, "Too tired to attack!")
                    return  # Don't flip turn
                damage, crit, miss = result["damage"], result["crit"], result["miss"]
                msg = ("Player missed!" if miss else
                       f"Critical hit! Player deals {damage} damage." if crit else
                       f"Player deals {damage} damage.")
            elif action == 'heal':
                if not self.player.has_potion():
                    add_to_log(self.battle_log, "No potions left!")
                    return  # Don't flip turn
                heal_amount = self.player.use_potion()
                if heal_amount > 0:
                    potion_count = sum(1 for item in self.player.inventory
                                     if isinstance(item, HealingPotion))
                    msg = f"Player uses potion for {heal_amount} HP! ({potion_count} left)"
                else:
                    msg = "No potions left!"
            elif action == 'defend':
                self.player.defend()
                msg = "Player braces for the next attack, gaining 1 stamina."
            add_to_log(self.battle_log, msg)
            self.meta.turns += 1
            self.player_turn = False

    def enemy_action(self):
        """Executes the enemy's action and returns the message."""
        if self.player_turn:
            return

        # AI: Decide whether to defend
        should_defend = (
            self.enemy.stamina == 0 or
            (self.enemy.health < self.enemy.max_health * 0.35 and random.random() < 0.25)
        )

        if should_defend:
            self.enemy.defend()
            add_to_log(self.battle_log, f"{self.enemy.name} is defending!")
        else:
            # Attack action
            result = self.enemy.attack_action(self.player)
            damage, crit, miss = result["damage"], result["crit"], result["miss"]
            if miss:
                msg = f"{self.enemy.name} missed!"
            elif crit:
                msg = f"Critical hit! {self.enemy.name} deals {damage} damage."
            else:
                msg = f"{self.enemy.name} deals {damage} damage."
            add_to_log(self.battle_log, msg)
        self.meta.turns += 1
        self.player_turn = True

    def update(self, signals: dict) -> None:
        """Runs one frame of battle logic."""
        if not self.player_turn and self.enemy.is_alive():
            self.enemy_action()

        if self.player_turn:
            if self.item_menu_open:
                self._handle_item_menu(signals)
            else:
                self._handle_player_actions(signals)

        self.check_battle_status()

    def _handle_item_menu(self, signals):
        """Handle input when the item menu is open."""
        if signals.get("number_keys"):
            key = signals["number_keys"][0]
            result = handle_item_use(self.player, key, lambda msg: add_to_log(self.battle_log, msg))
            if result.get("success"):
                self.item_menu_open = False
                self.player_turn = False
        elif signals.get("use_item"):
            self.item_menu_open = False

    def _handle_player_actions(self, signals: dict) -> None:
        """Handle player actions when the item menu is closed."""
        action_taken = None
        if signals.get("attack"):
            action_taken = 'attack'
        elif signals.get("defend"):
            action_taken = 'defend'
        elif signals.get("use_item"):
            self._toggle_item_menu()

        if action_taken:
            self.player_action(action_taken)
        elif signals.get("flee"):
            self._attempt_flee()

    def check_battle_status(self) -> None:
        """Checks if the battle is over and transitions to the next state."""
        from .victory import VictoryState  # Lazy import
        from .game_over import GameOverState # Lazy import

        if not self.enemy.is_alive():
            self._handle_victory()
            self.machine.change(
                VictoryState(self.player, self.meta, self.screen, self.battle_log)
            )
        elif not self.player.is_alive():
            add_to_log(self.battle_log, "Player has been defeated!")
            self.machine.change(
                GameOverState(self.player, self.meta, self.screen, self.battle_log)
            )

    def _handle_victory(self):
        """Handles the logic for when the player wins a battle."""
        xp_award = max(1, (self.enemy.encounter_index + 1) * 10)
        gold_award = (self.enemy.encounter_index + 1) * 5
        self.player.gain_xp(xp_award)
        self.player.gain_gold(gold_award)
        self.meta.battles_won += 1
        add_to_log(self.battle_log, f"You have defeated the {self.enemy.name}!")
        add_to_log(self.battle_log, f"You gain {xp_award} XP and {gold_award} gold.")

        if random.random() < 0.10:
            potion = HealingPotion()
            self.player.add_item(potion)
            add_to_log(self.battle_log, f"The enemy dropped {potion.name}!")

    def _toggle_item_menu(self) -> None:
        """Opens or closes the item menu."""
        if self.player.inventory:
            self.item_menu_open = not self.item_menu_open
        else:
            add_to_log(self.battle_log, "Inventory is empty.")

    def _attempt_flee(self) -> None:
        """Handles the player's attempt to flee from battle."""
        from .explore import ExploreState  # Lazy import to avoid circular dependency

        if random.random() <= config.FLEE_SUCCESS_PROB:
            add_to_log(self.battle_log, "Fled successfully!")
            self.meta.reset()  # Reset encounter metadata
            self.machine.change(ExploreState(self.player, self.meta, self.screen))
        else:
            add_to_log(self.battle_log, "Flee failed!")
            self.player_turn = False

    def render(self, screen) -> None:
        """Renders the battle screen."""
        render_battle_screen(screen, self)
        if self.item_menu_open:
            UI.render_item_menu(screen, self.player)
