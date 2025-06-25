"""Defines status effects that can be applied to entities."""
from abc import ABC, abstractmethod
import math

class Status(ABC):
    """Abstract base class for status effects."""
    name: str = ""
    icon_key: str = ""

    def __init__(self, duration: int):
        self.duration = duration

    @abstractmethod
    def on_apply(self, entity) -> None:
        """No immediate effect on apply."""

    @abstractmethod
    def on_turn_start(self, entity, battle_state) -> None:
        """Called at the start of the entity's turn."""

    @abstractmethod
    def on_expire(self, entity) -> None:
        """Called when the status duration reaches zero and is removed."""

    def tick(self, entity, battle_state) -> bool:
        """
        Process a single tick of the status effect.

        Returns True if the status expired this tick, False otherwise.
        """
        self.on_turn_start(entity, battle_state)
        self.duration -= 1
        if self.is_expired():
            self.on_expire(entity)
            return True
        return False

    def is_expired(self) -> bool:
        """Return True if the status effect has expired."""
        return self.duration <= 0

    def __repr__(self) -> str:
        return f"{self.name}({self.duration})"

class PoisonStatus(Status):
    """Deals percentage-based damage each turn."""
    name = "poison"
    icon_key = "icons/poison"
    PCT_DAMAGE = 0.06

    def on_apply(self, entity) -> None:
        """No immediate effect on apply."""

    def on_turn_start(self, entity, battle_state) -> None:
        damage = math.ceil(entity.max_health * self.PCT_DAMAGE)
        entity.deal_true_damage(damage)

        from src.utils import add_to_log
        add_to_log(battle_state.battle_log, f"{entity.name} suffers {damage} from poison.")

    def on_expire(self, entity) -> None:
        """No effect on expiration."""

class BleedStatus(Status):
    """Deals flat damage each turn."""
    name = "bleed"
    icon_key = "icons/bleed"
    FLAT_DAMAGE = 4

    def on_apply(self, entity) -> None:
        """No immediate effect on apply."""

    def on_turn_start(self, entity, battle_state) -> None:
        entity.deal_true_damage(self.FLAT_DAMAGE)

        from src.utils import add_to_log
        add_to_log(battle_state.battle_log, f"{entity.name} suffers {self.FLAT_DAMAGE} from bleeding.")

    def on_expire(self, entity) -> None:
        """No effect on expiration."""

class StunStatus(Status):
    """Prevents the entity from acting for a turn."""
    name = "stun"
    icon_key = "icons/stun"

    def on_apply(self, entity) -> None:
        entity.stunned = True

    def on_turn_start(self, entity, battle_state) -> None:
        """No recurring effect; stun blocks action directly."""

    def on_expire(self, entity) -> None:
        entity.stunned = False

class RegenerationStatus(Status):
    """Heals the entity for a flat amount each turn."""
    name = "regeneration"
    icon_key = "icons/regeneration"
    FLAT_HEAL = 4

    def on_apply(self, entity) -> None:
        """No immediate effect on apply."""

    def on_turn_start(self, entity, battle_state) -> None:
        entity.heal(self.FLAT_HEAL)
        
        from src.utils import add_to_log
        add_to_log(battle_state.battle_log, f"{entity.name} regenerates {self.FLAT_HEAL} HP.")

    def on_expire(self, entity) -> None:
        """No effect on expiration."""

__all__ = [
    "Status",
    "PoisonStatus",
    "BleedStatus",
    "StunStatus",
    "RegenerationStatus",
]
