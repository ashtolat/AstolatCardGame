# src/game/utils.py

import pygame
import os


def get_card(assets_path, filename, card_width, card_height, scale_factor, suit, value):
    """
    Get a specific card image from a spritesheet based on suit and value.
    """
    # Load the spritesheet
    image_path = os.path.join(assets_path, filename)
    spritesheet = pygame.image.load(image_path).convert_alpha()

    # Corrected suits mapping based on the provided order
    suits = {
        'Hearts': 0,
        'Diamonds': 1,
        'Spades': 2,
        'Clubs': 3,
        'Jester': 4,
        'Back': 5,
    }

    # Define values and their corresponding column indices
    values = {
        'Ace': 0,
        '2': 1,
        '3': 2,
        '4': 3,
        '5': 4,
        '6': 5,
        '7': 6,
        '8': 7,
        '9': 8,
        '10': 9,
        'Jack': 10,
        'Queen': 11,
        'King': 12,
        'Black Jester': 0,
        'Red Jester': 1,
        'Back': 0,
    }

    suit_index = suits.get(suit)
    value_index = values.get(value)

    if suit_index is None or value_index is None:
        raise ValueError(f"Invalid suit or value: {suit}, {value}")

    x = value_index * card_width
    y = suit_index * card_height

    rect = pygame.Rect(x, y, card_width, card_height)
    card_image = spritesheet.subsurface(rect)

    scaled_image = pygame.transform.scale(
        card_image, (card_width * scale_factor, card_height * scale_factor)
    )

    return scaled_image
