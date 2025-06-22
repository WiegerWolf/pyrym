"""
events.py
Handles user input and game events.
"""
import pygame
# pylint: disable=no-member

def process_events():
    """
    Process pygame events and return a dictionary of game actions.
    This version is simplified to eliminate the need for a separate
    event-handling function inside the BattleState, reducing complexity.
    """
    events = {
        "quit": False,
        "attack": False,
        "defend": False,
        "use_item": False,
        "flee": False,
        "cheat_gold": False,
        "number_keys": [],
    }

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            events["quit"] = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a or event.key == pygame.K_SPACE:
                events["attack"] = True
            if event.key == pygame.K_s:  # (S)earch, continue exploring
                events["attack"] = True
            elif event.key == pygame.K_d:
                events["defend"] = True
            elif event.key == pygame.K_i:
                events["use_item"] = True
            elif event.key == pygame.K_g:
                events["cheat_gold"] = True
            elif event.key == pygame.K_f:
                events["flee"] = True
            # For selecting items in the item menu
            elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                                 pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8,
                                 pygame.K_9]:
                    events["number_keys"].append(event.key)


    return events
