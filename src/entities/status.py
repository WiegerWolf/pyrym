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
        """Called when the status is applied to an entity."""
        pass

    @abstractmethod
    def on_turn_start(self, entity, battle_state) -> None:
        """Called at the start of the entity's turn."""
        pass

    @abstractmethod
    def on_expire(self, entity) -> None:
        """Called when the status duration reaches zero and is removed."""
        pass

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
    name = "poison"
    icon_key = "icons/poison"
    PCT_DAMAGE = 0.06

    def on_apply(self, entity) -> None:
        pass

    def on_turn_start(self, entity, battle_state) -> None:
        damage = math.ceil(entity.max_health * self.PCT_DAMAGE)
        entity.deal_true_damage(damage)

    def on_expire(self, entity) -> None:
        pass

class BleedStatus(Status):
    name = "bleed"
    icon_key = "icons/bleed"
    FLAT_DAMAGE = 4

    def on_apply(self, entity) -> None:
        pass

    def on_turn_start(self, entity, battle_state) -> None:
        entity.deal_true_damage(self.FLAT_DAMAGE)

    def on_expire(self, entity) -> None:
        pass

class StunStatus(Status):
    name = "stun"
    icon_key = "icons/stun"

    def on_apply(self, entity) -> None:
        entity.stunned = True

    def on_turn_start(self, entity, battle_state) -> None:
        pass

    def on_expire(self, entity) -> None:
        entity.stunned = False

class RegenerationStatus(Status):
    name = "regeneration"
    icon_key = "icons/regeneration"
    FLAT_HEAL = 4

    def on_apply(self, entity) -> None:
        pass

    def on_turn_start(self, entity, battle_state) -> None:
        entity.heal(self.FLAT_HEAL)

    def on_expire(self, entity) -> None:
        pass

__all__ = [
    "Status",
    "PoisonStatus",
    "BleedStatus",
    "StunStatus",
    "RegenerationStatus",
]