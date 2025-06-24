"""
Mini-event framework for ExploreState.
Defines base class, concrete stubs, and probability-based selection logic.
"""
from __future__ import annotations

import random
from abc import ABC, abstractmethod
from random import Random
from typing import TYPE_CHECKING, Type

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
        """Return True if this event decides to trigger given RNG."""

    def execute(self, player: "Entity", meta: dict, log: "BattleLog") -> str:
        """Apply side-effects, return description string."""

class TrapEvent(MiniEvent):
    """Player springs a trap."""

    @classmethod
    def roll(cls, rng: Random) -> bool:
        """Return True if this event decides to trigger given RNG."""

    def execute(self, player: "Entity", meta: dict, log: "BattleLog") -> str:
        """Apply side-effects, return description string."""

class FriendlyNPCEvent(MiniEvent):
    """Player meets a friendly NPC."""

    @classmethod
    def roll(cls, rng: Random) -> bool:
        """Return True if this event decides to trigger given RNG."""

    def execute(self, player: "Entity", meta: dict, log: "BattleLog") -> str:
        """Apply side-effects, return description string."""

class PuzzleEvent(MiniEvent):
    """Player discovers a puzzle."""

    @classmethod
    def roll(cls, rng: Random) -> bool:
        """Return True if this event decides to trigger given RNG."""

    def execute(self, player: "Entity", meta: dict, log: "BattleLog") -> str:
        """Apply side-effects, return description string."""

class GoldCacheEvent(MiniEvent):
    """Player finds a cache of gold."""

    @classmethod
    def roll(cls, rng: Random) -> bool:
        """Return True if this event decides to trigger given RNG."""

    def execute(self, player: "Entity", meta: dict, log: "BattleLog") -> str:
        """Apply side-effects, return description string."""

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


__all__ = [
    "trigger_random",
    "choose_event",
    "MiniEvent",
    "ItemFindEvent",
    "TrapEvent",
    "FriendlyNPCEvent",
    "PuzzleEvent",
    "GoldCacheEvent",
]
