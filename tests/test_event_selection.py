"""
Tests for mini-event probability and selection logic.
"""

from collections import Counter
from random import Random

from src.events.mini_events import (
    EVENT_TABLE,
    FriendlyNPCEvent,
    GoldCacheEvent,
    ItemFindEvent,
    PuzzleEvent,
    TrapEvent,
    choose_event,
)


def test_event_selection_distribution():
    """
    Verify that `choose_event` selects events respecting their defined
    weights over a large number of trials.
    """
    seed = 12345
    num_trials = 10_000
    rng = Random(seed)

    # Simulate many choices
    selections = [choose_event(rng) for _ in range(num_trials)]
    counts = Counter(selections)

    # Assert that each event was selected at least once
    expected_events = {event_class for event_class, _ in EVENT_TABLE}
    assert set(counts.keys()) == expected_events

    # Verify observed frequencies are within an acceptable tolerance
    for event_class, weight in EVENT_TABLE:
        expected_freq = weight
        observed_freq = counts[event_class] / num_trials
        # 3% absolute tolerance
        assert abs(observed_freq - expected_freq) <= 0.03, (
            f"Frequency for {event_class.__name__} deviates too much: "
            f"Expected ~{expected_freq:.2f}, got {observed_freq:.2f}"
        )


def test_event_classes_match_table():
    """Ensure EVENT_TABLE includes all and only the correct event types."""
    # Note: This is more of a sanity check for the test itself.
    table_events = {cls for cls, _ in EVENT_TABLE}
    expected_events = {
        ItemFindEvent,
        TrapEvent,
        FriendlyNPCEvent,
        PuzzleEvent,
        GoldCacheEvent,
    }
    assert table_events == expected_events
