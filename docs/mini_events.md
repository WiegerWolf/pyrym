# Mini-Events System

This document outlines the developer-facing details of the procedural mini-event system triggered during the `ExploreState`. This system is designed to introduce variety and unpredictability to the exploration phase of the game.

## Architecture Overview

The mini-event system is centered around a few core components in the `src/events/` directory.

- **`MiniEvent` ABC**: The abstract base class, [`MiniEvent`](src/events/mini_events.py:23), defines the contract for all mini-events. It has two key methods:
    - [`roll(cls, rng)`](src/events/mini_events.py:28): A class method that returns `True` or `False`, determining if the event should trigger after being selected. This allows for events that don't always happen.
    - [`execute(self, player, meta, log)`](src/events/mini_events.py:32): An instance method that applies the event's side-effects (e.g., giving an item, inflicting damage) and returns a descriptive string for the event log.

- **Concrete Subclasses**: Specific events like [`ItemFindEvent`](src/events/mini_events.py:36), [`TrapEvent`](src/events/mini_events.py:58), and [`FriendlyNPCEvent`](src/events/mini_events.py:77) inherit from `MiniEvent` and implement the `execute` logic. Most currently use a simple `roll` method that always returns `True`.

- **`EVENT_TABLE`**: A list in [`src/events/mini_events.py`](src/events/mini_events.py:126) that serves as a registry for all possible mini-events and their associated probability weights.
  ```python
  EVENT_TABLE: list[tuple[type[MiniEvent], float]] = [
      (ItemFindEvent, 0.35),
      (TrapEvent, 0.25),
      # ... and so on
  ]
  ```

- **Weighted Selection Algorithm**: The [`choose_event()`](src/events/mini_events.py:136) function implements a weighted random selection based on the `EVENT_TABLE`. It calculates the sum of all weights, picks a random number in that range, and then iterates through the table to find which event "owns" that slice of the total, making events with higher weights more likely to be chosen.

- **`ExploreState` Hook**: The exploration loop in [`src/states/explore.py`](src/states/explore.py:76) contains the trigger logic. On each exploration turn, it rolls against `config.MINI_EVENT_BASE_CHANCE`. If this roll succeeds, it calls [`trigger_random()`](src/events/mini_events.py:162) to run the full selection and execution process.
  ```python
  # In ExploreState._explore_turn()
  if random.random() < config.MINI_EVENT_BASE_CHANCE:
      desc = trigger_random(self.player, self.meta, self.log)
      if desc:
          add_to_log(self.log, desc)
          return  # mini-event consumes the turn
  ```

## Adding a New Event

To add a new mini-event, follow these steps:

1.  **Create a subclass** of `MiniEvent` in [`src/events/mini_events.py`](src/events/mini_events.py).
    ```python
    class MyNewEvent(MiniEvent):
        # ...
    ```
2.  **Implement the `execute` method** to define its behavior and return a log message.
    ```python
    def execute(self, player: "Entity", meta: dict, log: "BattleLog") -> str:
        message = "Something amazing happened!"
        # apply effects to player...
        utils.add_to_log(log, message)
        return message
    ```
3.  **Register the event** by adding it to the `EVENT_TABLE` with a desired weight. The engine will automatically incorporate it into the selection logic.
    ```python
    EVENT_TABLE: list[tuple[type[MiniEvent], float]] = [
        (ItemFindEvent, 0.35),
        # ...
        (MyNewEvent, 0.05), # Make it rare
    ]
    ```
    Alternatively, for events defined in other modules, you can use the [`register_event()`](src/events/mini_events.py:196) helper function at runtime.

4.  **Update weights** of existing events if necessary to ensure the total probability distribution remains as intended.

5.  **(Optional) Add tests** for the new event's side-effects, or update the distribution test if applicable.

## Probability & Tuning

Event trigger frequency is controlled by two mechanisms:

1.  **Global Trigger Chance**: The [`MINI_EVENT_BASE_CHANCE`](src/config.py:126) in [`config.py`](src/config.py) is a float (e.g., `0.20`) that determines the chance of *any* mini-event occurring on a given exploration step. This is the master gate.

2.  **Individual Event Weight**: Once the global trigger passes, the `EVENT_TABLE` determines which specific event occurs. The probability of an event is its weight divided by the sum of all weights.

Here is the current table from [`mini_events.py`](src/events/mini_events.py:126):

| Event Class        | Weight | Cumulative Chance |
| ------------------ | ------ | ----------------- |
| `ItemFindEvent`    | 0.35   | 35%               |
| `TrapEvent`        | 0.25   | 60%               |
| `FriendlyNPCEvent` | 0.15   | 75%               |
| `PuzzleEvent`      | 0.15   | 90%               |
| `GoldCacheEvent`   | 0.10   | 100%              |
| **Total**          | **1.00** |                   |


## Testing Strategy

The primary test for the event system is [`tests/test_event_selection.py`](tests/test_event_selection.py). This file contains:

- A distribution check, [`test_event_selection_distribution()`](tests/test_event_selection.py:19), which runs the [`choose_event()`](src/events/mini_events.py:136) function thousands of times with a fixed seed to verify that the selection frequency of each event aligns with its assigned weight, within a reasonable tolerance.
- A sanity check to ensure the `EVENT_TABLE` contains the expected set of events.

Currently, tests for the specific side-effects of each event's `execute` method are not implemented. These are planned for a future development step (Step 10).

## Extensibility Notes

- **UI Feedback**: For events that need to provide immediate, prominent visual feedback beyond the text log, the [`flash_message()`](src/core/ui.py:202) helper in [`src/core/ui.py`](src/core/ui.py) can be used to display large, centered text on the screen for a short duration.
- **Future Hooks**: The `MiniEvent.execute` method signature is simple, but can be expanded. Future work might include passing an `animation_manager` to allow events to trigger custom particle effects or screen shakes.