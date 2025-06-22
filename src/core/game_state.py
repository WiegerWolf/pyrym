from enum import Enum, auto


class GameState(Enum):
    """Enumeration of possible high-level game states."""
    BATTLE = auto()
    EXPLORE = auto()
    GAME_OVER = auto()


class StateManager:
    """
    Lightweight holder for the current game state.
    Uses a module-level (class) attribute to avoid the need
    for explicit instantiation at this stage of the refactor.
    """
    _current_state: GameState = GameState.BATTLE

    @classmethod
    def get_state(cls) -> GameState:
        """Return the current game state."""
        return cls._current_state

    @classmethod
    def set_state(cls, state: GameState) -> None:
        """Set the current game state."""
        cls._current_state = state
