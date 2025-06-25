"""
Tests for the side-effects of mini-events.
"""

from collections import Counter
from random import Random
from typing import List
import pytest

from src.entities.base import Entity
from src.entities.status import PoisonStatus, BleedStatus
from src.events.mini_events import (
    EVENT_TABLE,
    WEIGHT_SUM,
    FriendlyNPCEvent,
    GoldCacheEvent,
    TrapEvent,
    choose_event,
)
from src.items import Antidote, HealingPotion


# pylint: disable=redefined-outer-name,too-few-public-methods
class MockBattleState:
    """A mock battle state to pass to status effect ticks."""
    def __init__(self, log):
        self.battle_log = log

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
        self.inventory = []

    def add_item(self, item):
        """Mock method for adding items to the player's inventory."""
        self.inventory.append(item)

    def gain_gold(self, amount: int):
        """Mock method for gaining gold."""
        self.gold += amount

    def regenerate_stamina(self):
        """Mock method for regenerating stamina."""
        self.stamina = min(self.stamina + 1, self.max_stamina)


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
    assert log.messages[0] == f"You found a cache of {gold_gain} gold!"


def test_poison_tick_logs_message(player: DummyPlayer, log: MockLog):
    """Verify that a poison tick adds a message to the battle log."""
    mock_state = MockBattleState(log)
    poison = PoisonStatus(duration=3)
    player.apply_status(poison)

    # The first tick happens on turn start
    player.tick_statuses(mock_state)

    assert len(log.messages) == 1, "A log message should have been generated"
    assert "suffers" in log.messages[0], "The log message should describe poison damage"
    assert "poison" in log.messages[0], "The log message should mention poison"


def test_antidote_item_cures_poison(player: DummyPlayer):
    """Verify that using an Antidote item removes negative status effects."""
    player.apply_status(PoisonStatus(duration=3))
    player.apply_status(BleedStatus(duration=2))
    antidote = Antidote()

    assert len(player.statuses) == 2, "Statuses should be applied before curing"

    result = antidote.use(player)

    assert len(player.statuses) == 0, "Antidote should clear all negative statuses"
    assert result["value"] == 2, "The use-result should report two statuses cleared"
    assert "curing" in result["message"], "Success message should be returned"


def test_friendly_npc_cures_and_heals(player: DummyPlayer, log: MockLog):
    """
    Verify the FriendlyNPCEvent clears negative statuses AND heals the player.
    """
    player.health = 20  # Start with low health
    player.apply_status(PoisonStatus(duration=3))
    initial_health = player.health

    event = FriendlyNPCEvent()
    message = event.execute(player, {}, log)

    assert player.health > initial_health, "Player should be healed"
    assert len(player.statuses) == 0, "Player statuses should be cleared"
    assert "cures your ailments" in message, "Event message should mention curing"
    assert "heals you" in message, "Event message should mention healing"


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
def test_poison_ticks_in_explore_mode(player: DummyPlayer, monkeypatch):
    """Verify poison deals damage and expires during exploration."""
    from src.states.explore import ExploreState
    from src.entities.status import PoisonStatus

    # Prevent encounters and mini-events from happening
    monkeypatch.setattr("random.random", lambda: 0.9)
    def mock_trigger_random(*args, **kwargs):
        return ""
    monkeypatch.setattr("src.states.explore.trigger_random", mock_trigger_random)

    initial_health = player.health
    poison = PoisonStatus(duration=3)
    player.apply_status(poison)

    class MockMeta:
        encounter_index = 0

    explore_state = ExploreState(player, MockMeta(), None)
    
    # Simulate 3 steps in explore mode
    for _ in range(3):
        explore_state._explore_turn()

    damage_per_tick = player.max_health * PoisonStatus.PCT_DAMAGE
    expected_health = initial_health - (damage_per_tick * 3)
    
    # Use math.isclose for float comparison
    import math
    assert math.isclose(player.health, expected_health), "Player health not reduced correctly"
    assert not player.has_status(PoisonStatus), "Poison status should have expired"

def test_poison_ticks_once_per_battle_turn(player: DummyPlayer, log: MockLog):
    """Verify poison deals damage only once per turn in battle."""
    from src.states.battle import BattleState
    from src.entities.status import PoisonStatus
    from src.entities.enemy import Enemy
    
    initial_health = player.health
    poison = PoisonStatus(duration=3)
    player.apply_status(poison)

    enemy = Enemy(1)
    battle_state = BattleState(player, enemy, {}, None)
    battle_state.battle_log = log.messages

    # Simulate one frame update
    battle_state.update({})

    damage_per_tick = player.max_health * PoisonStatus.PCT_DAMAGE
    expected_health = initial_health - damage_per_tick

    import math
    assert math.isclose(player.health, expected_health), "Player health not reduced correctly"
    
    status = next((s for s in player.statuses if isinstance(s, PoisonStatus)), None)
    assert status is not None and status.duration == 2, "Poison duration not updated correctly"