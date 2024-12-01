# src/game/deck.py

import random
from card import Card


class Deck:
    def __init__(self, assets_path):
        self.cards = []
        self.discard_pile = []

        suits = ['Hearts', 'Diamonds', 'Spades', 'Clubs']
        values = ['Ace', '2', '3', '4', '5', '6', '7',
                  '8', '9', '10']  # Exclude 'Jack', 'Queen', 'King'

        for suit in suits:
            for value in values:
                self.cards.append(Card(suit, value, assets_path))

        # If Jesters are to be included in the deck
        # self.cards.append(Card('Jester', 'Black Jester', assets_path))
        # self.cards.append(Card('Jester', 'Red Jester', assets_path))

        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, num_cards=1):
        drawn_cards = []
        for _ in range(num_cards):
            if not self.cards:
                # Reshuffle discard pile into deck
                self.cards.extend(self.discard_pile)
                self.shuffle()
                self.discard_pile.clear()
            if self.cards:
                drawn_cards.append(self.cards.pop())
        return drawn_cards

    def discard(self, card):
        self.discard_pile.append(card)
