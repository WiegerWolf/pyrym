import pygame

def process_events():
    """
    Process pygame events and return a dictionary of game actions.
    """
    events = {
        "quit": False,
        "player_action_ready": False,
        "player_action_type": None,
        "enter_explore": False,
        "return_battle": False
    }

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            events["quit"] = True
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                events["player_action_ready"] = True
                events["player_action_type"] = 'attack'
            elif event.key == pygame.K_p:
                events["player_action_ready"] = True
                events["player_action_type"] = 'heal'
            elif event.key == pygame.K_d:
                events["player_action_ready"] = True
                events["player_action_type"] = 'defend'
            elif event.key == pygame.K_e:
                events["enter_explore"] = True
            elif event.key == pygame.K_b:
                events["return_battle"] = True


    return events