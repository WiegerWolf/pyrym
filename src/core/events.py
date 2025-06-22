import pygame

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
        "heal": False,
        "flee": False,
        "p": False # For ExploreState potion use
    }

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            events["quit"] = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                events["attack"] = True
            elif event.key == pygame.K_d:
                events["defend"] = True
            elif event.key == pygame.K_p:
                events["heal"] = True
                events["p"] = True
            elif event.key == pygame.K_f:
                events["flee"] = True
                
    return events