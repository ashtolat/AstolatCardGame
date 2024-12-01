# src/game/player.py

from card import Card


class Player:
    def __init__(self, name, assets_path):
        self.name = name
        self.hand = []
        self.assets_path = assets_path

        # Top cards (e.g., Jack, Queen, King)
        self.top_cards = [
            {'name': 'Jack', 'health': 15, 'max_health': 15},
            {'name': 'Queen', 'health': 25, 'max_health': 25},
            {'name': 'King', 'health': 40, 'max_health': 40},
        ]
        self.current_top_card_index = 0

        # Defense status
        self.defense_active = False

    def draw_cards(self, deck, num_cards):
        """Draw a specified number of cards from the deck."""
        new_cards = deck.draw(num_cards)
        self.hand.extend(new_cards)

    def play_card(self, index):
        """Play a card from the player's hand."""
        if index < 0 or index >= len(self.hand):
            raise IndexError("Invalid card index.")
        return self.hand.pop(index)

    def receive_damage(self, damage):
        """Receive damage to the current top card."""
        current_top_card = self.top_cards[self.current_top_card_index]
        current_top_card['health'] -= damage

        # If top card is defeated, move to the next
        if current_top_card['health'] <= 0:
            current_top_card['health'] = 0
            self.current_top_card_index += 1

    def is_defeated(self):
        """Check if all top cards are defeated."""
        return self.current_top_card_index >= len(self.top_cards)
