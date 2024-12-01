# src/game/main.py

import pygame
import os
from menu import Menu

def main():
    pygame.init()
    screen = pygame.display.set_mode((1200, 600))
    pygame.display.set_caption('Astolat Card Game')
    try:
        menu = Menu(screen)
        menu.display_menu()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        pygame.quit()

if __name__ == '__main__':
    main()
