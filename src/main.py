import pygame
import config
from game import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption(config.GAME_TITLE)
    
    game = Game(screen)
    game.run()

    pygame.quit()

if __name__ == "__main__":
    main()