import pygame
from game import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Turn-Based Game")
    
    game = Game(screen)
    game.run()

    pygame.quit()

if __name__ == "__main__":
    main()