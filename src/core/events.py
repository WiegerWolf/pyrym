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
    }

    for event in raw_events:
        if event.type == pygame.QUIT:
            events["quit"] = True

        if event.type == pygame.KEYDOWN:
            # Battle / General
            if event.key == pygame.K_a:
                events["attack"] = True
            elif event.key == pygame.K_d:
                events["defend"] = True
            elif event.key == pygame.K_i:
                events["use_item"] = True
            elif event.key == pygame.K_f:
                events["flee"] = True

            # Explore
            elif event.key == pygame.K_e:
                events["explore"] = True

            # Shop
            elif event.key == pygame.K_q:
                events["quit_shop"] = True

            # Universal number keys
            elif event.key in [
                pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8,
                pygame.K_9
            ]:
                events["number_keys"].append(event.key)

    events["raw_events"] = raw_events
    return events
