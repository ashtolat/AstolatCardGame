# src/game/ai_player.py

import random
from card import Card


class AIPlayer:
    def __init__(self, name, assets_path, difficulty='Easy'):
        self.name = name
        self.hand = []
        self.assets_path = assets_path
        self.difficulty = difficulty

        # Top cards (e.g., Jack, Queen, King)
        self.top_cards = [
            {'name': 'Jack', 'health': 15, 'max_health': 15},
            {'name': 'Queen', 'health': 25, 'max_health': 25},
            {'name': 'King', 'health': 40, 'max_health': 40},
        ]
        self.current_top_card_index = 0

        # Defense status
        self.defense_active = False

        # Jesters (if used in your game)
        self.jesters = 2

    def draw_cards(self, deck, num_cards):
        """Draw a specified number of cards from the deck."""
        new_cards = deck.draw(num_cards)
        self.hand.extend(new_cards)

    def play_card(self, index):
        """Play a card from the AI's hand."""
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

    def decide_action(self, player_top_card):
        """
        Decide which card to play based on difficulty.

        :param player_top_card: The player's current top card.
        :return: The selected card to play.
        """
        if not self.hand:
            return None

        if self.difficulty == 'Easy':
            return self.easy_behavior()
        elif self.difficulty == 'Medium':
            return self.medium_behavior(player_top_card)
        elif self.difficulty == 'Hard':
            return self.hard_behavior(player_top_card)
        else:
            # Default to Easy behavior if difficulty is unrecognized
            return self.easy_behavior()

    def easy_behavior(self):
        """Easy AI behavior: Randomly selects a card to play."""
        # Filter attack cards (e.g., non-healing, non-defensive)
        attack_cards = [card for card in self.hand if card.suit != 'Diamonds']
        if attack_cards:
            selected_card = random.choice(attack_cards)
            self.hand.remove(selected_card)
            return selected_card
        else:
            # If no attack cards, play any available card
            selected_card = random.choice(self.hand)
            self.hand.remove(selected_card)
            return selected_card

    def medium_behavior(self, player_top_card):
        """Medium AI behavior: Maximizes short-term gains."""
        if not player_top_card:
            # If player top card is not available, default to Easy behavior
            return self.easy_behavior()

        # Analyze own top card health
        own_top_card = self.top_cards[self.current_top_card_index]
        own_health_ratio = own_top_card['health'] / own_top_card['max_health']

        # Prioritize attacking if opponent's face card is weak
        player_health_ratio = player_top_card['health'] / player_top_card['max_health']

        # Decide whether to attack or defend/heal
        if own_health_ratio < 0.3:
            # If own health is low, consider healing or defense
            heal_cards = [card for card in self.hand if card.suit == 'Hearts']
            defense_cards = [card for card in self.hand if card.suit == 'Diamonds']

            # Prefer healing over defense
            if heal_cards:
                selected_card = max(heal_cards, key=lambda c: c.get_attack_value())
                self.hand.remove(selected_card)
                return selected_card
            elif defense_cards:
                selected_card = max(defense_cards, key=lambda c: c.get_attack_value())
                self.hand.remove(selected_card)
                return selected_card

        # If opponent's health is low, attempt to finish them off
        if player_health_ratio < 0.3:
            attack_cards = [card for card in self.hand if card.suit != 'Hearts']
            if attack_cards:
                # Use the strongest attack card
                selected_card = max(attack_cards, key=lambda c: c.get_attack_value())
                self.hand.remove(selected_card)
                return selected_card

        # Otherwise, conserve powerful cards and use moderate attacks
        moderate_attack_cards = [card for card in self.hand if 4 <= card.get_attack_value() <= 7]
        if moderate_attack_cards:
            selected_card = random.choice(moderate_attack_cards)
            self.hand.remove(selected_card)
            return selected_card
        else:
            # If no moderate cards, play any attack card
            attack_cards = [card for card in self.hand if card.suit != 'Hearts']
            if attack_cards:
                selected_card = min(attack_cards, key=lambda c: c.get_attack_value())
                self.hand.remove(selected_card)
                return selected_card

        # If no attack cards, play any available card
        selected_card = random.choice(self.hand)
        self.hand.remove(selected_card)
        return selected_card

    def hard_behavior(self, player_top_card):
        """Hard AI behavior: Uses advanced strategies and predictive modeling."""
        if not player_top_card:
            # If player top card is not available, default to Medium behavior
            return self.medium_behavior(player_top_card)

        # Analyze own top card and player's top card
        own_top_card = self.top_cards[self.current_top_card_index]
        own_health_ratio = own_top_card['health'] / own_top_card['max_health']
        player_health_ratio = player_top_card['health'] / player_top_card['max_health']

        # Predictive modeling (simplified for this context)
        # Assume player may have high-damage cards if hand size > 3
        potential_threat = len(self.hand) > 3

        # Decide whether to defend
        if potential_threat and own_health_ratio < 0.6:
            defense_cards = [card for card in self.hand if card.suit == 'Diamonds']
            if defense_cards:
                selected_card = max(defense_cards, key=lambda c: c.get_attack_value())
                self.hand.remove(selected_card)
                return selected_card

        # Use Jesters strategically
        if self.jesters > 0 and own_health_ratio < 0.3:
            # Use a Jester to refresh hand or heal (implement according to your game rules)
            self.jesters -= 1
            # Assuming Jester allows drawing new cards
            # Implement Jester logic in your game (e.g., draw new cards)
            # For now, we'll skip the action and proceed
            pass

        # Optimize use of high-value cards
        high_value_attack_cards = [card for card in self.hand if card.get_attack_value() >= 8]
        if player_health_ratio < 0.5 and high_value_attack_cards:
            # Use high-value card to deal significant damage
            selected_card = max(high_value_attack_cards, key=lambda c: c.get_attack_value())
            self.hand.remove(selected_card)
            return selected_card

        # Balance offensive and defensive strategies
        if own_health_ratio < 0.5:
            # Consider healing
            heal_cards = [card for card in self.hand if card.suit == 'Hearts']
            if heal_cards:
                selected_card = max(heal_cards, key=lambda c: c.get_attack_value())
                self.hand.remove(selected_card)
                return selected_card

        # Default to moderate attacks
        moderate_attack_cards = [card for card in self.hand if 5 <= card.get_attack_value() <= 10]
        if moderate_attack_cards:
            selected_card = max(moderate_attack_cards, key=lambda c: c.get_attack_value())
            self.hand.remove(selected_card)
            return selected_card

        # If no other options, play any available card
        selected_card = random.choice(self.hand)
        self.hand.remove(selected_card)
        return selected_card
