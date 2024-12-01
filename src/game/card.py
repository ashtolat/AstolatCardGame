# src/game/card.py

from utils import get_card


class Card:
    def __init__(self, suit, value, assets_path):
        self.suit = suit
        self.value = value

        # Load big image
        self.big_card_width = 48
        self.big_card_height = 64
        self.big_scale_factor = 3
        self.big_image = get_card(
            assets_path, 'bigcards.png',
            self.big_card_width, self.big_card_height,
            self.big_scale_factor, suit, value
        )

        # Load mini image
        self.mini_card_width = 15
        self.mini_card_height = 22
        self.mini_scale_factor = 4
        self.mini_image = get_card(
            assets_path, 'minicards.png',
            self.mini_card_width, self.mini_card_height,
            self.mini_scale_factor, suit, value
        )

    def get_attack_value(self):
        # Define attack values based on card value
        if self.value in ['Jack', 'Queen', 'King']:
            return 10  # Face cards shouldn't be in hand
        elif self.value == 'Ace':
            return 1
        elif self.value in ['Black Jester', 'Red Jester']:
            return 0  # Adjust based on game rules
        else:
            return int(self.value)
