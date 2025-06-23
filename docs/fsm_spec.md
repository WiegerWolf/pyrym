# Finite State Machine (FSM) Specification

## Goals
1. Replace scattered `if/elif` transition logic with a dedicated FSM.  
2. Provide reliable `enter` / `exit` hooks for every state.  
3. Centralise transitions so each state can trigger the next without the core loop knowing the details.  
4. Keep design simple; no push/pop stack or hierarchy (can be added later).  

## File Layout
* [`src/core/state_machine.py`](src/core/state_machine.py:1) – FSM engine and `BaseState`.  
* Existing state files (`src/states/*.py`) will inherit from `BaseState`.  
* Core loop updates:  
  * [`src/core/game.py`](src/core/game.py:20) will hold a `StateMachine` instance.  

## API Design

### BaseState (abstract)

| Method | Arguments | Returns | Responsibility |
| ------ | --------- | ------- | -------------- |
| `enter(prev_state, **kwargs)` | `prev_state` (BaseState or `None`), additional data | `None` | Initialise the state, load resources, prepare UI. |
| `exit(next_state)` | `next_state` (BaseState) | `None` | Clean up resources, stop timers, etc. |
| `handle_events(events)` | Raw pygame events list | `None` | Process immediate events (key down, mouse, etc.). |
| `update(signals)` | Pre-processed input dict | `dict` (optional status) | Run one frame of logic. |
| `render(screen)` | Pygame surface | `None` | Draw the frame. |

Concrete state classes (`ExploreState`, `BattleState`, etc.) implement these hooks.

### StateMachine

```python
class StateMachine:
    def __init__(self, initial_state: BaseState) -> None
    def change(self, new_state: BaseState, **kwargs) -> None
    def current(self) -> BaseState
    def handle_events(self, events) -> None
    def update(self, signals) -> None
    def render(self, screen) -> None
```

*Change workflow*  
1. Current state's `exit(new_state)` is called.  
2. `self._state = new_state`  
3. New state's `enter(prev_state, **kwargs)` is called.  

### Transition Examples
* `BattleState` detects victory → `self.machine.change(VictoryState(...))`  
* `VictoryState` button press → `self.machine.change(ShopState(...))`  
* `GameOverState` restart → re-initialise `StateMachine` with `ExploreState`.  

## Game Loop Integration

In [`Game.run()`](src/core/game.py:40):

```python
signals = process_events()
events = signals["raw_events"]

self.machine.handle_events(events)
self.machine.update(signals)
self.machine.render(self.screen)
```

## Migration Steps
1. Create `state_machine.py` with `BaseState` + `StateMachine`.  
2. Refactor each current state class to inherit from `BaseState`.  
3. Remove `GameState` enum and `StateManager`.  
4. Update `game.py` core loop to use the machine.  
5. Delete dead code and run tests.  

## Future Extensions
* **Stack-based push/pop:** Implement `_stack: list[BaseState]` and delegate calls to the top state (`push()`, `pop()`).  
* **Hierarchical FSM:** Allow states to have a `parent` and bubble events upward.