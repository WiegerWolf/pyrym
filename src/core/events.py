"""
events.py
Handles user input and game events.
"""
import pygame
# pylint: disable=no-member

def process_events():
    """
    Process pygame events and return a dictionary of game actions.
    """
    raw_events = pygame.event.get()
    events = {
        "quit": False,
        "attack": False,
        "defend": False,
        "use_item": False,
        "flee": False,
        "number_keys": [],
        "quit_shop": False,
        "explore": False,
        "skill_q": False,
        "skill_w": False,
        "skill_e": False,
        "skill_r": False,
    }

    for event in raw_events:
        if event.type == pygame.QUIT:
            events["quit"] = True

        if event.type == pygame.KEYDOWN:
            key_is_mapped = False

            # Mappings that don't conflict
            keymap = {
                pygame.K_a: "attack",
                pygame.K_d: "defend",
                pygame.K_i: "use_item",
                pygame.K_f: "flee",
                pygame.K_w: "skill_w",
                pygame.K_r: "skill_r",
            }
            action = keymap.get(event.key)
            if action:
                events[action] = True
                key_is_mapped = True

            # Handle context-dependent keys by flagging all possible actions.
            # The game state manager is responsible for choosing the correct one.
            if event.key == pygame.K_q:
                events["quit_shop"] = True
                events["skill_q"] = True
                key_is_mapped = True

            if event.key == pygame.K_e:
                events["explore"] = True
                events["skill_e"] = True
                key_is_mapped = True

            # Number keys are a fallback option.
            if not key_is_mapped and event.key in [
                pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8,
                pygame.K_9,
            ]:
                events["number_keys"].append(event.key)

    events["raw_events"] = raw_events
    return events
