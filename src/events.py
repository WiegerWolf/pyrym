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
        "c": False,
        "b": False,
        "p": False,
    }

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            events["quit"] = True
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                events["player_action_ready"] = True
                events["player_action_type"] = 'attack'
            elif event.key == pygame.K_p:
                events["p"] = True
            elif event.key == pygame.K_d:
                events["player_action_ready"] = True
                events["player_action_type"] = 'defend'
            elif event.key == pygame.K_e:
                events["enter_explore"] = True
            elif event.key == pygame.K_b:
                events["b"] = True
            elif event.key == pygame.K_c:
                events["c"] = True


    return events