"""
game_state.py
Defines and manages game states.
"""
from enum import Enum, auto


class GameState(Enum):
    """Enumeration of possible high-level game states."""
    BATTLE = auto()
    EXPLORE = auto()
    SHOP = auto()
    GAME_OVER = auto()


class StateManager:
    """
    Lightweight holder for the current game state.
    Uses a module-level (class) attribute to avoid the need
    for explicit instantiation at this stage of the refactor.
    """
    _current_state: GameState = GameState.EXPLORE
    gold: int = 0
    # Holds flags for one-time purchases, e.g. {"max_hp_blessing": True}
    purchased_flags: dict[str, bool] = {}

    @classmethod
    def get_state(cls) -> GameState:
        """Return the current game state."""
        return cls._current_state

    @classmethod
    def set_state(cls, state: GameState) -> None:
        """Set the current game state."""
        cls._current_state = state

    @classmethod
    def adjust_gold(cls, delta: int) -> None:
        """Safely adjust player gold."""
        cls.gold = max(0, cls.gold + delta)
        print(f"Adjusted gold by {delta}. New balance: {cls.gold}")
