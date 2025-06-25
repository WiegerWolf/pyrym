"""
Mini-event framework for ExploreState.

Defines a base class for events, several concrete event implementations,
probability-based selection logic, and a runtime extension hook
(`register_event`) for other systems to add their own events.
"""
from __future__ import annotations

import random
from abc import ABC, abstractmethod
from random import Random, randint
from typing import TYPE_CHECKING, Type

from src import utils, items
from src.entities.status import PoisonStatus


if TYPE_CHECKING:  # avoid circulars
    from src.entities.base import Entity
    from src.core.battle_log import BattleLog

class MiniEvent(ABC):
    """Abstract mini-event invoked during exploration."""

    @classmethod
    @abstractmethod
    def roll(cls, rng: Random) -> bool:
        """Return True if this event decides to trigger given RNG."""

    @abstractmethod
    def execute(self, player: "Entity", meta: dict, log: "BattleLog") -> str:
        """Apply side-effects, return description string."""

# Concrete stubs — logic comes in Step 4
class ItemFindEvent(MiniEvent):
    """Player finds a random item."""

    @classmethod
    def roll(cls, rng: Random) -> bool:
        """This event always triggers if selected."""
        return True

    def execute(self, player: "Entity", meta: dict, log: "BattleLog") -> str:
        """Generates and awards a random item to the player."""
        loot = random.choice([items.HealingPotion(), items.GoldPile(randint(5, 20))])
        if not loot.can_store:
            loot.use(player)
            message = f"You found {loot.amount} gold!"
        else:
            player.add_item(loot)
            message = f"You found a {loot.name}."

        utils.add_to_log(log, message)
        return message


class TrapEvent(MiniEvent):
    """Player springs a trap."""

    @classmethod
    def roll(cls, rng: Random) -> bool:
        """This event always triggers if selected."""
        return True

    def execute(self, player: "Entity", meta: dict, log: "BattleLog") -> str:
        """A 50/50 chance to take damage or get poisoned."""
        if random.random() < 0.5:
            damage = randint(5, 15)
            utils.inflict_damage(player, damage, log)
            message = f"It's a trap! You took {damage} damage."
        else:
            utils.give_status(player, PoisonStatus, duration=3, log_callback=log)
            message = "It's a trap! You have been poisoned."
 
        # Ensure the trap description itself is logged exactly once
        utils.add_to_log(log, message)
        return message


class FriendlyNPCEvent(MiniEvent):
    """Player meets a friendly NPC."""

    @classmethod
    def roll(cls, rng: Random) -> bool:
        """This event always triggers if selected."""
        return True

    def execute(self, player: "Entity", meta: dict, log: "BattleLog") -> str:
        """A friendly traveler heals you."""
        heal_amount = int(player.max_health * 0.20)
        player.heal(heal_amount)
        message = f"A friendly traveler heals you for {heal_amount} HP."
        utils.add_to_log(log, message)
        return message


class PuzzleEvent(MiniEvent):
    """Player discovers a puzzle."""

    @classmethod
    def roll(cls, rng: Random) -> bool:
        """This event always triggers if selected."""
        return True

    def execute(self, player: "Entity", meta: dict, log: "BattleLog") -> str:
        """You solve a simple riddle and gain XP (stub)."""
        # player.gain_xp(20)  # Assuming player has a gain_xp method.
        message = "You solve a simple riddle and feel more experienced."
        utils.add_to_log(log, message)
        return message


class GoldCacheEvent(MiniEvent):
    """Player finds a cache of gold."""

    @classmethod
    def roll(cls, rng: Random) -> bool:
        """This event always triggers if selected."""
        return True

    def execute(self, player: "Entity", meta: dict, log: "BattleLog") -> str:
        """You find a cache of gold."""
        amount = randint(5, 30)
        player.gain_gold(amount)
        if log is not None:
            utils.add_to_log(log, f"You found {amount} gold!")
        message = f"You found a cache of {amount} gold!"
        # Log the flavour text separately so players see both lines
        utils.add_to_log(log, message)
        return message

# Probability and selection logic
EVENT_TABLE: list[tuple[type[MiniEvent], float]] = [
    (ItemFindEvent, 0.35),
    (TrapEvent, 0.25),
    (FriendlyNPCEvent, 0.15),
    (PuzzleEvent, 0.15),
    (GoldCacheEvent, 0.10),
]
WEIGHT_SUM = sum(w for _, w in EVENT_TABLE)


def choose_event(rng: Random | None = None) -> Type[MiniEvent]:
    """
    Select a mini-event class from the event table based on assigned weights.
    Uses cumulative weight calculation for selection.

    Args:
        rng: An optional `random.Random` instance for deterministic testing.
             If None, the global `random` module is used.

    Returns:
        The selected `MiniEvent` subclass.
    """
    if rng is None:
        rng = random

    roll = rng.uniform(0, WEIGHT_SUM)
    cumulative_weight = 0.0
    for event_class, weight in EVENT_TABLE:
        cumulative_weight += weight
        if roll < cumulative_weight:
            return event_class

    # Fallback in case of floating point inaccuracies, though unlikely.
    return EVENT_TABLE[-1][0]


def trigger_random(
    player: "Entity", meta: dict, log: "BattleLog", rng: Random | None = None
) -> str:
    """
    Select, instantiate, and execute a random mini-event.

    1. Chooses an event class using weighted probability.
    2. Instantiates the chosen event.
    3. Calls its `roll()` method; if it returns False, the event does not trigger.
    4. If the roll passes, calls `execute()` and returns the resulting description.

    Args:
        player: The player entity.
        meta: Game metadata dictionary.
        log: The battle/event log.
        rng: An optional `random.Random` instance for deterministic testing.
             If None, the global `random` module is used.

    Returns:
        A description of the event that occurred, or an empty string if no
        event triggered.
    """
    if rng is None:
        rng = random

    event_class = choose_event(rng)
    event_instance = event_class()

    if not event_instance.roll(rng):
        return ""

    return event_instance.execute(player, meta, log)


def register_event(event_cls: type[MiniEvent], weight: float) -> None:
    """
    Dynamically add a MiniEvent subclass to the EVENT_TABLE.

    Args:
        event_cls: Concrete subclass to register.
        weight: Probability weight to assign.
    """
    if not issubclass(event_cls, MiniEvent):
        raise TypeError("Must register a MiniEvent subclass.")
    EVENT_TABLE.append((event_cls, weight))
    global WEIGHT_SUM  # pylint: disable=global-statement
    WEIGHT_SUM += weight


__all__ = [
    "trigger_random",
    "choose_event",
    "register_event",
    "MiniEvent",
    "ItemFindEvent",
    "TrapEvent",
    "FriendlyNPCEvent",
    "PuzzleEvent",
    "GoldCacheEvent",
]
