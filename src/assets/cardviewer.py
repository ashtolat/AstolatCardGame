import pygame
import sys

pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
BIG_CARD_WIDTH = 48
BIG_CARD_HEIGHT = 64
MINI_CARD_WIDTH = 15
MINI_CARD_HEIGHT = 22
SCALE_FACTOR_BIG = 3  # Scaling factor for big cards
SCALE_FACTOR_MINI = 6  # Scaling factor for mini cards
SPACE_BETWEEN_CARDS = 50  # Space between big and mini cards
FPS = 60

# Setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Card Viewer")

def load_cards(filename, width, height, scale_factor, card_counts):
    spritesheet = pygame.image.load(filename).convert_alpha()
    cards = []
    for row in range(len(card_counts)):
        for col in range(card_counts[row]):
            x = col * width
            y = row * height
            card = pygame.Surface((width, height), pygame.SRCALPHA)
            card.blit(spritesheet, (0, 0), (x, y, width, height))
            scaled_card = pygame.transform.scale(card, (width * scale_factor, height * scale_factor))
            cards.append(scaled_card)
    return cards

# load cards
big_card_counts = [13, 13, 13, 13, 10]  # Number of cards in each row for big cards
mini_card_counts = [13, 13, 13, 13, 2]  # Number of cards in each row for mini cards, only 2 jesters
big_cards = load_cards('bigcards.png', BIG_CARD_WIDTH, BIG_CARD_HEIGHT, SCALE_FACTOR_BIG, big_card_counts)
mini_cards = load_cards('minicards.png', MINI_CARD_WIDTH, MINI_CARD_HEIGHT, SCALE_FACTOR_MINI, mini_card_counts)

# number of cards to display in viewer (excluding card backs)
total_cards_to_display = sum(mini_card_counts) - (mini_card_counts[-1] - 2)

# card index
current_card = 0

# Main loop
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                current_card = (current_card - 1) % total_cards_to_display
            if event.key == pygame.K_RIGHT:
                current_card = (current_card + 1) % total_cards_to_display

    # Fill the screen with black
    screen.fill((0, 0, 0))

    # Calculate positions for big and mini cards
    big_card_pos_x = SCREEN_WIDTH / 2 - BIG_CARD_WIDTH * SCALE_FACTOR_BIG - SPACE_BETWEEN_CARDS
    mini_card_pos_x = SCREEN_WIDTH / 2 + SPACE_BETWEEN_CARDS

    # Draw the current big and mini card
    screen.blit(big_cards[current_card], (big_card_pos_x, SCREEN_HEIGHT // 2 - BIG_CARD_HEIGHT * SCALE_FACTOR_BIG // 2))
    screen.blit(mini_cards[current_card], (mini_card_pos_x, SCREEN_HEIGHT // 2 - MINI_CARD_HEIGHT * SCALE_FACTOR_MINI // 2))

    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

pygame.quit()
sys.exit()
