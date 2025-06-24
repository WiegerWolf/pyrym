"""
Tests for the side-effects of mini-events.
"""

from collections import Counter
from random import Random
from typing import List
import pytest

from src.entities.base import Entity
from src.entities.status import PoisonStatus
from src.events.mini_events import (
    EVENT_TABLE,
    WEIGHT_SUM,
    GoldCacheEvent,
    TrapEvent,
    choose_event,
)

# pylint: disable=redefined-outer-name,too-few-public-methods
class MockLog:
    """A simple, mutable object to act as a log for testing."""
    def __init__(self):
        self.messages: List[str] = []

    def append(self, message: str):
        """Adds a message to the internal list."""
        self.messages.append(message)

    def __len__(self):
        return len(self.messages)

    def __bool__(self):
        """Ensure the mock log object is always considered 'truthy'."""
        return True


class DummyPlayer(Entity):
    """A lightweight player stub for testing event side-effects."""
    def __init__(self, name="Dummy", health=100, attack=10):
        super().__init__(name, health, attack)
        self.gold = 100  # Starting gold for tests

    def add_item(self, item):
        """Mock method for tests."""
        # This method is required by the Entity interface but not used here.
        # The 'item' parameter is kept for signature compatibility.
        _ = item


@pytest.fixture
def player():
    """Provides a fresh dummy player instance for each test."""
    return DummyPlayer()


@pytest.fixture
def log():
    """Provides a fresh mock log for each test."""
    return MockLog()


def test_trap_event_effect(player: DummyPlayer, log: MockLog, monkeypatch):
    """
    Verify a TrapEvent either deals damage or applies poison.
    """
    # Force a specific RNG outcome for the trap's effect
    rng = Random(1)  # This seed causes damage
    monkeypatch.setattr("random.random", rng.random)
    monkeypatch.setattr("random.randint", rng.randint)

    event = TrapEvent()
    initial_hp = player.health
    event.execute(player, {}, log)

    hp_lost = initial_hp - player.health
    poisoned = player.has_status(PoisonStatus)

    assert hp_lost > 0 or poisoned, "Trap did not inflict damage or poison"

    # Now test the poison outcome with a different seed
    player = DummyPlayer()  # Reset player
    rng = Random(2)  # This seed causes poison
    monkeypatch.setattr("random.random", rng.random)

    event.execute(player, {}, log)
    assert player.has_status(PoisonStatus), "Trap failed to apply poison"


def test_gold_award_range(player: DummyPlayer, log: MockLog, monkeypatch):
    """
    Verify GoldCacheEvent awards an amount within the expected range.
    """
    # Monkeypatch the randint call inside execute
    def mock_randint(min_val, max_val):
        assert min_val == 5
        assert max_val == 30
        return 15  # A fixed value within the range
    monkeypatch.setattr("src.events.mini_events.randint", mock_randint)

    event = GoldCacheEvent()
    initial_gold = player.gold

    # Execute the event, which should call the logging util.
    message = event.execute(player, {}, log)

    gold_gain = player.gold - initial_gold
    assert 5 <= gold_gain <= 30, "Gold gain is outside the expected range"

    # Check the event's return message
    assert message == f"You found a cache of {gold_gain} gold!"

    # Check that the log fixture was populated by the helper function.
    assert len(log.messages) > 0, "The log should have received a message"
    assert log.messages[0] == f"You found {gold_gain} gold!"


def test_event_distribution_stability():
    """
    Verify that `choose_event` adheres to weights over a very large sample,
    using a different seed to ensure robustness.
    """
    seed = 2025
    num_trials = 20_000
    rng = Random(seed)

    selections = [choose_event(rng) for _ in range(num_trials)]
    counts = Counter(selections)

    assert len(counts) == len(EVENT_TABLE)

    for event_class, weight in EVENT_TABLE:
        expected_freq = weight / WEIGHT_SUM
        observed_freq = counts[event_class] / num_trials
        assert abs(observed_freq - expected_freq) <= 0.03, (
            f"Frequency for {event_class.__name__} deviates too much: "
            f"Expected ~{expected_freq:.3f}, got {observed_freq:.3f} "
            f"(Weight: {weight}, Count: {counts[event_class]})"
        )