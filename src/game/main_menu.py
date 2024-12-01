import pygame
import pygame_gui
import sys

# Initialize Pygame and Pygame_gui
pygame.init()
pygame.display.set_caption('Astolat Card Game')

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
window_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Colors and settings
background_color = pygame.Color('#25292e')
manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT), 'theme.json')

# Clock
clock = pygame.time.Clock()
FPS = 60

def main_menu():
    # Create buttons
    start_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 100, 250), (200, 50)),
        text='Start',
        manager=manager
    )

    rules_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 100, 325), (200, 50)),
        text='Rules',
        manager=manager
    )

    exit_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 100, 400), (200, 50)),
        text='Exit',
        manager=manager
    )

    running = True
    while running:
        time_delta = clock.tick(FPS)/1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == start_button:
                    print("Start Game")
                elif event.ui_element == rules_button:
                    print("Show Rules")
                elif event.ui_element == exit_button:
                    pygame.quit()
                    sys.exit()

            manager.process_events(event)

        manager.update(time_delta)

        window_surface.fill(background_color)
        manager.draw_ui(window_surface)

        pygame.display.flip()

if __name__ == "__main__":
    main_menu()
