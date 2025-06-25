"""Provides a clean public API for triggering and registering mini-events."""

from .mini_events import trigger_random, register_event  # re-export

__all__ = ["trigger_random", "register_event"]
