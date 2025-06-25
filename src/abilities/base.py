"""
base.py
Base class for all abilities.
"""
from __future__ import annotations
import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..entities.base import Entity

class Ability(abc.ABC):  # pylint: disable=too-few-public-methods
    """Base class for all abilities."""

    def __init__(self, name: str, stamina_cost: int = 0, base_cooldown: int = 0):
        self.name = name
        self.stamina_cost = stamina_cost
        self.base_cooldown = base_cooldown

    def on_use(self, actor: Entity):
        """
        Register this ability’s cool-down on the acting Entity.
        """
        actor.cooldowns[self.name] = self.base_cooldown

    @abc.abstractmethod
    def execute(self, actor: Entity, target: Entity | None = None) -> dict:
        """
        Execute the ability.

        :param actor: The entity performing the action.
        :param target: The entity being targeted.
        :return: A dictionary containing the results of the action.
        """
        raise NotImplementedError
