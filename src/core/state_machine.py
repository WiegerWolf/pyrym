"""
state_machine.py
Provides a robust finite-state machine (FSM) for managing game states.
"""
from typing import Optional


class BaseState:
    """
    Abstract base class for all game states.
    Defines the interface that the StateMachine uses to manage states.
    """

    def __init__(self):
        self.machine: Optional["StateMachine"] = None

    def enter(self, prev_state: "BaseState", **kwargs) -> None:
        """
        Called when this state becomes the active state.
        :param prev_state: The state that was previously active.
        :param kwargs: Optional data passed from the previous state.
        """

    def exit(self, next_state: "BaseState") -> None:
        """
        Called when this state is no longer active.
        :param next_state: The state that will become active.
        """

    def handle_events(self, events) -> None:
        """
        Process raw pygame events.
        :param events: A list of pygame events.
        """

    def update(self, signals: dict) -> None:
        """
        Update state logic based on pre-processed signals.
        :param signals: A dictionary of input signals.
        """

    def render(self, screen) -> None:
        """
        Render the state to the screen.
        :param screen: The pygame screen surface.
        """


class StateMachine:
    """
    Manages a collection of states and the transitions between them.
    """

    def __init__(self, initial_state: BaseState):
        self._state: Optional[BaseState] = None
        self.change(initial_state)

    def change(self, new_state: BaseState, **kwargs) -> None:
        """
        Transitions from the current state to a new one.
        :param new_state: The state to transition to.
        :param kwargs: Optional data to pass to the new state's enter() method.
        """
        prev_state = self._state
        if self._state:
            self._state.exit(new_state)

        new_state.machine = self
        self._state = new_state
        self._state.enter(prev_state, **kwargs)

    @property
    def current(self) -> Optional[BaseState]:
        """Returns the currently active state."""
        return self._state

    def handle_events(self, events) -> None:
        """Delegates event handling to the current state."""
        if self._state:
            self._state.handle_events(events)

    def update(self, signals: dict) -> None:
        """Delegates logic updates to the current state."""
        if self._state:
            self._state.update(signals)

    def render(self, screen) -> None:
        """Delegates rendering to the current state."""
        if self._state:
            self._state.render(screen)