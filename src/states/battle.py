"""BattleState: turn-based combat state with status-effect integration."""
# pylint: disable=too-many-instance-attributes, attribute-defined-outside-init
# pylint: disable=cyclic-import
import random

from .. import config
from ..core.state_machine import BaseState
from ..core.ui import render_battle_screen
from ..entities.status import StunStatus  # status helpers
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
        self.player_turn = True
        self.battle_log = []
        self.ticked_this_turn = False

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
        if self._check_stun_and_flip(self.player, "Player"):
            return
        msg = ""  # Default message if no action is taken
        if self.player_turn:
            if action == 'attack':
                result = self.player.attack_action(self.enemy)
                if result.get("no_stamina"):
                    add_to_log(self.battle_log, "Too tired to attack!")
                    return  # Don't flip turn
                damage, crit, miss = result["damage"], result["crit"], result["miss"]
                if miss:
                    msg = "Player missed!"
                elif crit:
                    msg = f"Critical hit! Player deals {damage} damage."
                else:
                    msg = f"Player deals {damage} damage."
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
            self.ticked_this_turn = False

    def enemy_action(self):
        """Executes the enemy's action and returns the message."""
        if self._check_stun_and_flip(self.enemy, self.enemy.name):
            return
        if self.player_turn:
            return

        # C. Enemy AI skill usage
        ready_skills = [s for s in self.enemy.skills if self.enemy.ability_ready(s.name)]
        skill_to_use = None
        if ready_skills:
            for skill in ready_skills:
                if skill.name == "Shield Bash" and any(
                    isinstance(st, StunStatus) for st in self.player.statuses
                ):
                    continue
                skill_to_use = skill
                break  # Use the first available skill

        if skill_to_use:
            skill_to_use.execute(self.enemy, self.player, self)
            add_to_log(self.battle_log, f"{self.enemy.name} uses {skill_to_use.name}.")
            self.meta.turns += 1
            self.player_turn = True
            self.ticked_this_turn = False
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
        self.ticked_this_turn = False

    def _check_stun_and_flip(self, actor, name: str) -> bool:
        """Return True if actor is stunned and the turn was skipped."""
        if actor.has_status(StunStatus):
            add_to_log(self.battle_log, f"{name} is stunned and cannot act!")
            # do not consume stamina; simply end turn
            self.player_turn = not self.player_turn
            self.ticked_this_turn = False
            self.meta.turns += 1
            return True
        return False

    def update(self, signals: dict) -> None:
        """Runs one frame of battle logic."""
        if not self.ticked_this_turn:
            actor = self.player if self.player_turn else self.enemy
            actor.tick_statuses(self)
            actor.tick_cooldowns()
            self.ticked_this_turn = True

        # Tick active status effects for the acting entity
        if not self.player_turn and self.enemy.is_alive():
            self.enemy_action()

        if self.player_turn:
            self._handle_player_actions(signals)

        self.check_battle_status()

    def _handle_player_actions(self, signals: dict) -> None:
        """Handle player actions."""
        action_taken = None
        skill_key = None
        for key in ('q', 'w', 'e', 'r'):
            if signals.get(f"skill_{key}"):
                skill_key = key
                break

        if signals.get("attack"):
            action_taken = 'attack'
        elif signals.get("defend"):
            action_taken = 'defend'
        elif skill_key:
            skill = self.player.get_skill_for_key(skill_key)
            if skill and self.player.ability_ready(skill.name):
                skill.execute(self.player, self.enemy, self)
                add_to_log(self.battle_log, f"Player uses {skill.name}.")
                self.meta.turns += 1
                self.player_turn = False
                self.ticked_this_turn = False
            else:
                add_to_log(self.battle_log, "Skill is on cool-down!")
        elif signals.get("number_keys"):
            key = signals["number_keys"][0]
            result = handle_item_use(self.player, key, lambda msg: add_to_log(self.battle_log, msg))
            if result.get("success"):
                self.player_turn = False
                self.ticked_this_turn = False

        if action_taken:
            self.player_action(action_taken)
        elif signals.get("flee"):
            self._attempt_flee()

    def check_battle_status(self) -> None:
        """Checks if the battle is over and transitions to the next state."""
        # pylint: disable=import-outside-toplevel
        from .game_over import GameOverState
        from .victory import VictoryState

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
        self.meta.encounter_index += 1
        add_to_log(self.battle_log, f"You have defeated the {self.enemy.name}!")
        log_msg = f"You gain {xp_award} XP and {gold_award} gold."
        add_to_log(self.battle_log, log_msg)

        if random.random() < 0.10:
            potion = HealingPotion()
            self.player.add_item(potion)
            add_to_log(self.battle_log, f"The enemy dropped {potion.name}!")

    def _attempt_flee(self) -> None:
        """Handles the player's attempt to flee from battle."""
        # pylint: disable=import-outside-toplevel
        from .explore import ExploreState

        if random.random() <= config.FLEE_SUCCESS_PROB:
            add_to_log(self.battle_log, "Fled successfully!")
            self.meta.reset()  # Reset encounter metadata
            self.machine.change(ExploreState(self.player, self.meta, self.screen))
        else:
            add_to_log(self.battle_log, "Flee failed!")
            self.player_turn = False
            self.ticked_this_turn = False

    def render(self, screen) -> None:
        """Renders the battle screen."""
        render_battle_screen(screen, self)

        # After main battle screen is drawn, overlay status icons
        self._render_status_icons(screen)

    def _render_status_icons(self, screen):
        """Renders status icons for both player and enemy."""
        from ..core.ui import render_status_icons  # pylint: disable=import-outside-toplevel
        render_status_icons(screen, self.player, (50, 100))
        render_status_icons(screen, self.enemy, (500, 100))
