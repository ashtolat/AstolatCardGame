# src/game/ai_player.py

import random
from card import Card

MAX_HAND_SIZE = 5 # maximum hand size


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

        # Jesters
        self.jesters = 2

    def draw_cards(self, deck, num_cards):
        """Draw a specified number of cards from the deck without exceeding MAX_HAND_SIZE."""
        available_space = MAX_HAND_SIZE - len(self.hand)
        num_to_draw = min(num_cards, available_space)
        if num_to_draw > 0:
            new_cards = deck.draw(num_to_draw)
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

    def decide_action(self, player_top_card, player_defense_active):
        """
        Decides the best action based on the AI's behavior level.
        """
        if self.hand:  # Ensure the hand is not empty
            if self.difficulty == 'Hard':
                return self.hard_behavior(player_top_card, player_defense_active)
            elif self.difficulty == 'Medium':
                return self.medium_behavior(player_top_card)
            else:
                return self.easy_behavior()
        else:
            return None  # No cards to play

    def easy_behavior(self):
        """
        Easy AI behavior: Randomly selects a card to play.
        """
        attack_cards = [card for card in self.hand if card.suit != 'Diamonds']
        if attack_cards:
            selected_card = random.choice(attack_cards)
        else:
            selected_card = random.choice(self.hand)
        self.hand.remove(selected_card)
        return selected_card

    def medium_behavior(self, player_top_card):
        """
        Medium AI behavior: Balances short-term gains and survival.
        """
        if not player_top_card:
            # If player top card is not available, default to Easy behavior
            return self.easy_behavior()

        # Analyze health ratios
        own_top_card = self.top_cards[self.current_top_card_index]
        own_health_ratio = own_top_card['health'] / own_top_card['max_health']
        player_health_ratio = player_top_card['health'] / player_top_card['max_health']

        # Heal or defend if health is low
        if own_health_ratio < 0.3:
            heal_cards = [card for card in self.hand if card.suit == 'Hearts']
            defense_cards = [card for card in self.hand if card.suit == 'Diamonds']
            if heal_cards:
                selected_card = max(heal_cards, key=lambda c: c.get_attack_value())
            elif defense_cards:
                selected_card = max(defense_cards, key=lambda c: c.get_attack_value())
            else:
                selected_card = random.choice(self.hand)  # Fallback
            self.hand.remove(selected_card)
            return selected_card

        # Attack with strong cards if player's health is low
        if player_health_ratio < 0.3:
            attack_cards = [card for card in self.hand if card.suit != 'Hearts']
            if attack_cards:
                selected_card = max(attack_cards, key=lambda c: c.get_attack_value())
                self.hand.remove(selected_card)
                return selected_card

        # Use moderate attacks or fallback to weak attacks
        attack_cards = sorted(
            (card for card in self.hand if card.suit != 'Hearts'),
            key=lambda c: c.get_attack_value()
        )
        if attack_cards:
            moderate_attacks = [card for card in attack_cards if 4 <= card.get_attack_value() <= 7]
            selected_card = random.choice(moderate_attacks) if moderate_attacks else attack_cards[0]
            self.hand.remove(selected_card)
            return selected_card

        # Fallback to any card
        selected_card = random.choice(self.hand)
        self.hand.remove(selected_card)
        return selected_card

    def hard_behavior(self, player_top_card, player_defense_active):
        """
        Hard AI behavior: Uses strategic decision-making.
        """
        if not player_top_card:
            # Default to Medium behavior if player_top_card is not available
            return self.medium_behavior(player_top_card)

        # Analyze health ratios
        own_top_card = self.top_cards[self.current_top_card_index]
        own_health = own_top_card['health']
        max_health = own_top_card['max_health']
        player_health = player_top_card['health']

        # Joker Logic: Refresh hand if all cards are low value
        average_card_value = sum(card.get_attack_value() for card in self.hand) / len(self.hand)
        if average_card_value < 4 and self.jesters > 0:
            self.jesters -= 1
            return "Use Jester"

        best_action = None
        best_score = float('-inf')

        # Evaluate all possible actions
        for card in self.hand:
            if card.suit == 'Hearts':  # Healing
                if own_health < max_health:
                    heal_amount = min(max_health - own_health, card.get_attack_value())
                    score = heal_amount * 2
                    if score > best_score:
                        best_score = score
                        best_action = card

            elif card.suit == 'Diamonds':  # Defense
                # Activate defense only if not already active
                if not self.defense_active and own_health < max_health * 0.6:
                    score = max_health - own_health
                    if player_defense_active:
                        score *= 0.5  # Decrease priority if the player is defending
                    if score > best_score:
                        best_score = score
                        best_action = card

            elif card.suit == 'Clubs':  # Double damage attack
                attack_value = card.get_attack_value() * 2
                overkill_penalty = max(0, attack_value - player_health)
                score = (player_health * 3) - overkill_penalty
                if score > best_score:
                    best_score = score
                    best_action = card

            elif card.suit == 'Spades':  # Combined attack
                for combo_card in self.hand:
                    if combo_card == card:
                        continue
                    combined_value = card.get_attack_value() + combo_card.get_attack_value()
                    overkill_penalty = max(0, combined_value - player_health)
                    score = (player_health * 4) - overkill_penalty
                    if combo_card.suit == 'Clubs':
                        double_damage_value = combo_card.get_attack_value() * 2
                        if double_damage_value > combined_value:
                            score -= double_damage_value
                    if score > best_score:
                        best_score = score
                        best_action = (card, combo_card)

            else:  # Basic attack
                attack_value = card.get_attack_value()
                overkill_penalty = max(0, attack_value - player_health)
                score = (player_health * 2) - overkill_penalty
                if score > best_score:
                    best_score = score
                    best_action = card

        # Execute best action
        if best_action:
            if isinstance(best_action, tuple):  # Spades combo
                spade, combo_card = best_action
                self.hand.remove(spade)
                self.hand.remove(combo_card)
                return spade, combo_card
            elif best_action.suit == 'Diamonds':
                # Activate defense when playing a Diamonds card
                self.defense_active = True
            self.hand.remove(best_action)
            return best_action

        # Fallback to any card
        selected_card = random.choice(self.hand)
        self.hand.remove(selected_card)
        return selected_card




    def get_hand_description(self):
        """Return a formatted string of the AI's current hand."""
        return ', '.join([f"{card.suit} {card.rank}" for card in self.hand])
