"""
base.py
Base class for all abilities.
"""
from __future__ import annotations
import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..entities.base import Entity

class Ability(abc.ABC):
    """Base class for all abilities."""

    def __init__(self, name: str):
        self.name = name

    @abc.abstractmethod
    def execute(self, actor: Entity, target: Entity | None = None) -> dict:
        """
        Execute the ability.

        :param actor: The entity performing the action.
        :param target: The entity being targeted.
        :return: A dictionary containing the results of the action.
        """
        raise NotImplementedError
