"""
Initializes the core game components package.
"""
from .game import Game
from .events import *
from .ui import UI
from .state_machine import StateMachine, BaseState
from .ui import render_battle_screen  # add below existing imports

__all__ = ["Game", "UI", "StateMachine", "BaseState"]
__all__.append("render_battle_screen")
