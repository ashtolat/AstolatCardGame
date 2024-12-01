# src/game/game.py

import pygame
import os
import random
from deck import Deck
from player import Player
from ai_player import AIPlayer
from utils import get_card
from button import Button


class Game:
    def __init__(self, screen, difficulty='Easy'):
        self.screen = screen
        self.difficulty = difficulty
        assets_path = self.get_assets_path()

        self.deck = Deck(assets_path)
        self.player = Player('Player', assets_path)
        self.ai_player = AIPlayer('AI', assets_path, difficulty=self.difficulty)

        self.current_turn = 'Player'
        self.running = True
        self.game_over = False

        self.font = pygame.font.Font(os.path.join(assets_path, 'font.ttf'), 24)
        self.small_font = pygame.font.Font(os.path.join(assets_path, 'font.ttf'), 18)
        self.background = pygame.image.load(
            os.path.join(assets_path, 'background.png')).convert()
        self.clock = pygame.time.Clock()
        self.message = ""
        self.defense_active = False

        # Card dimensions and scaling factors
        self.big_card_width = 48
        self.big_card_height = 64
        self.big_scale_factor = 3

        self.mini_card_width = 15
        self.mini_card_height = 22
        self.mini_scale_factor = 4

        # Load images for player's top cards (Hearts suit)
        self.top_card_images = {
            rank: get_card(
                assets_path, 'bigcards.png',
                self.big_card_width, self.big_card_height,
                self.big_scale_factor, 'Hearts', rank
            )
            for rank in ['Jack', 'Queen', 'King']
        }

        # Load images for AI's top cards (Spades suit)
        self.ai_top_card_images = {
            rank: get_card(
                assets_path, 'bigcards.png',
                self.big_card_width, self.big_card_height,
                self.big_scale_factor, 'Spades', rank
            )
            for rank in ['Jack', 'Queen', 'King']
        }

        # Extract card back images
        self.card_back_image = get_card(
            assets_path, 'bigcards.png',
            self.big_card_width, self.big_card_height,
            self.big_scale_factor, 'Back', 'Back'
        )
        self.mini_card_back_image = get_card(
            assets_path, 'minicards.png',
            self.mini_card_width, self.mini_card_height,
            self.mini_scale_factor, 'Back', 'Back'
        )

        # Load images for Jesters
        self.player_jester_image = get_card(
            assets_path, 'minicards.png',
            self.mini_card_width, self.mini_card_height,
            self.mini_scale_factor, 'Jester', 'Black Jester'
        )
        self.ai_jester_image = get_card(
            assets_path, 'minicards.png',
            self.mini_card_width, self.mini_card_height,
            self.mini_scale_factor, 'Jester', 'Red Jester'
        )

        # Initialize player's and AI's Jesters
        self.player_jesters = 2
        self.ai_jesters = 2

        # Create Jester buttons for the player
        self.player_jester_buttons = []
        self.create_player_jester_buttons()

        # Initialize action buttons list
        self.action_buttons = []

        # Initialize action history
        self.action_history = []

        # Initialize the toggle for showing AI's cards
        self.show_ai_cards = True

        # Create the "Show AI cards" toggle button
        self.show_ai_cards_button = Button(
            text="Hide AI cards" if self.show_ai_cards else "Show AI cards",
            x=10,
            y=self.screen.get_height() - 50,
            width=150,
            height=40,
            font=self.font,
            callback=self.toggle_show_ai_cards
        )

        # Create the "Back to Menu" button for the game over screen
        self.back_to_menu_button = Button(
            text="Back to Menu",
            x=(self.screen.get_width() - 200) // 2,
            y=self.screen.get_height() // 2 + 50,
            width=200,
            height=50,
            font=self.font,
            callback=self.back_to_menu
        )

        # Flags for Spades combo
        self.waiting_for_second_card = False
        self.selected_second_card_index = None

    def get_assets_path(self):
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, 'assets')

    def create_player_jester_buttons(self):
        self.player_jester_buttons.clear()
        jester_button_width = self.player_jester_image.get_width()
        jester_button_height = self.player_jester_image.get_height()
        for i in range(self.player_jesters):
            x = self.screen.get_width() - (jester_button_width + 10) * (i + 1)
            y = self.screen.get_height() - jester_button_height - 10
            button = Button(
                x=x,
                y=y,
                image=self.player_jester_image,
                callback=self.use_player_jester,
                args=[i]
            )
            self.player_jester_buttons.append(button)

    def toggle_show_ai_cards(self):
        self.show_ai_cards = not self.show_ai_cards
        if self.show_ai_cards:
            self.show_ai_cards_button.text = "Hide AI cards"
        else:
            self.show_ai_cards_button.text = "Show AI cards"

    def back_to_menu(self):
        self.running = False

    def use_player_jester(self, index):
        if self.player_jesters > 0:
            num_cards_needed = 5 - len(self.player.hand)
            if num_cards_needed > 0:
                self.player.hand.clear()
                self.player.draw_cards(self.deck, 5)
                self.display_message("You have refreshed your hand using a Jester!")
            else:
                self.display_message("Your hand is already full!")
            self.player_jesters -= 1
            self.create_player_jester_buttons()
            self.current_turn = 'AI'

    def start_game(self):
        self.player.draw_cards(self.deck, 5)
        self.ai_player.draw_cards(self.deck, 5)
        self.game_loop()

    def game_loop(self):
        while self.running:
            self.handle_events()
            self.update_game_state()
            self.render()
            self.clock.tick(60)

            if self.current_turn == 'Player' and not self.game_over:
                if not self.waiting_for_second_card and not self.action_buttons:
                    self.start_player_turn()
            elif self.current_turn == 'AI' and not self.game_over:
                pygame.time.delay(1000)  # Delay for 1 second before AI action
                self.start_ai_turn()

    def start_player_turn(self):
        if len(self.player.hand) < 5:
            self.player.draw_cards(self.deck, 1)
        if len(self.player.hand) == 0:
            self.player.draw_cards(self.deck, 5)
            self.display_message("Your hand was empty! Drawing 5 new cards.")
        

    def start_ai_turn(self):
        if len(self.ai_player.hand) < 5:
            self.ai_player.draw_cards(self.deck, 1)
        if len(self.ai_player.hand) == 0:
            self.ai_player.draw_cards(self.deck, 5)
            self.display_message("AI's hand was empty! AI draws 5 new cards.")
        self.ai_turn()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_over:
                    self.back_to_menu_button.handle_event(event)
                else:
                    pos = pygame.mouse.get_pos()
                    if self.current_turn == 'Player':
                        selected_card_index = self.get_card_at_pos(pos)
                        if selected_card_index is not None:
                            if self.waiting_for_second_card:
                                self.selected_second_card_index = selected_card_index
                            else:
                                self.player_turn(selected_card_index)
                    if self.action_buttons:
                        for button in self.action_buttons:
                            button.handle_event(event)
                    for button in self.player_jester_buttons:
                        button.handle_event(event)
                    self.show_ai_cards_button.handle_event(event)

    def update_game_state(self):
        if self.player.is_defeated():
            self.display_message("You have been defeated!")
            self.game_over = True
        elif self.ai_player.is_defeated():
            self.display_message("You have won the game!")
            self.game_over = True

    def render(self):
        if self.game_over:
            self.draw_game_over_screen()
            pygame.display.flip()
            return

        self.screen.blit(self.background, (0, 0))
        self.draw_ai_hand()
        self.draw_player_hand()
        self.draw_top_cards()
        self.draw_message()
        if self.action_buttons:
            for button in self.action_buttons:
                button.draw(self.screen)
        for button in self.player_jester_buttons:
            button.draw(self.screen)
        self.draw_ai_jesters()
        self.draw_action_history()
        self.show_ai_cards_button.draw(self.screen)
        pygame.display.flip()

    def draw_game_over_screen(self):
        self.screen.fill((0, 0, 0))
        message_surface = self.font.render(self.message, True, (255, 255, 255))
        message_rect = message_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(message_surface, message_rect)
        self.back_to_menu_button.draw(self.screen)

    def draw_ai_jesters(self):
        x = 10
        y = 10
        for i in range(self.ai_jesters):
            self.screen.blit(self.ai_jester_image,
                             (x + i * (self.ai_jester_image.get_width() + 10), y))

    def draw_action_history(self):
        x = self.screen.get_width() - 300
        y = 100
        line_height = 25
        for entry in reversed(self.action_history[-15:]):
            text_surface = self.small_font.render(entry, True, (255, 255, 255))
            self.screen.blit(text_surface, (x, y))
            y += line_height
            if y > self.screen.get_height() - line_height:
                break

    def add_action_to_history(self, message):
        self.action_history.append(message)
        if len(self.action_history) > 15:
            self.action_history.pop(0)

    def draw_player_hand(self):
        hand = self.player.hand
        if not hand:
            return
        card_spacing = 10
        card_width = hand[0].big_image.get_width()
        card_height = hand[0].big_image.get_height()
        total_width = len(hand) * card_width + (len(hand) - 1) * card_spacing
        start_x = (self.screen.get_width() - total_width) // 2
        base_y = self.screen.get_height() - (card_height // 2)

        mouse_pos = pygame.mouse.get_pos()
        for i, card in enumerate(hand):
            x = start_x + i * (card_width + card_spacing)
            card_rect = pygame.Rect(x, base_y, card_width, card_height)
            if card_rect.collidepoint(mouse_pos):
                y = base_y - 20
            else:
                y = base_y
            self.screen.blit(card.big_image, (x, y),
                             area=pygame.Rect(0, 0, card_width, card_height // 2 + 20))

    def draw_ai_hand(self):
        hand = self.ai_player.hand
        if not hand:
            return
        card_spacing = 10
        card_width = hand[0].mini_image.get_width()
        card_height = hand[0].mini_image.get_height()
        total_width = len(hand) * card_width + (len(hand) - 1) * card_spacing
        start_x = (self.screen.get_width() - total_width) // 2
        base_y = 10

        for i, card in enumerate(hand):
            x = start_x + i * (card_width + card_spacing)
            y = base_y
            if self.show_ai_cards:
                self.screen.blit(card.mini_image, (x, y))
            else:
                self.screen.blit(self.mini_card_back_image, (x, y))

    def draw_top_cards(self):
        player_top_card = self.player.top_cards[self.player.current_top_card_index]
        top_card_image = self.top_card_images[player_top_card['name']]
        x = self.screen.get_width() // 2 - top_card_image.get_width() - 100
        y = self.screen.get_height() // 2 - top_card_image.get_height() // 2
        self.screen.blit(top_card_image, (x, y))
        self.draw_health_bar(x, y - 20, player_top_card['health'], player_top_card['max_health'])
        health_text = f"{player_top_card['health']}/{player_top_card['max_health']}"
        health_surface = self.small_font.render(health_text, True, (255, 255, 255))
        self.screen.blit(health_surface, (x + 105, y - 25))

        ai_top_card = self.ai_player.top_cards[self.ai_player.current_top_card_index]
        top_card_image_ai = self.ai_top_card_images[ai_top_card['name']]
        x_ai = self.screen.get_width() // 2 + 100
        y_ai = self.screen.get_height() // 2 - top_card_image_ai.get_height() // 2
        self.screen.blit(top_card_image_ai, (x_ai, y_ai))
        self.draw_health_bar(x_ai, y_ai - 20, ai_top_card['health'], ai_top_card['max_health'])
        health_text_ai = f"{ai_top_card['health']}/{ai_top_card['max_health']}"
        health_surface_ai = self.small_font.render(health_text_ai, True, (255, 255, 255))
        self.screen.blit(health_surface_ai, (x_ai + 105, y_ai - 25))

    def draw_health_bar(self, x, y, current_health, max_health):
        bar_width = 100
        bar_height = 10
        fill = (current_health / max_health) * bar_width
        outline_rect = pygame.Rect(x, y, bar_width, bar_height)
        fill_rect = pygame.Rect(x, y, fill, bar_height)
        pygame.draw.rect(self.screen, (255, 0, 0), fill_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), outline_rect, 1)

    def get_card_at_pos(self, pos):
        hand = self.player.hand
        if not hand:
            return None
        card_spacing = 10
        card_width = hand[0].big_image.get_width()
        card_height = hand[0].big_image.get_height()
        total_width = len(hand) * card_width + (len(hand) - 1) * card_spacing
        start_x = (self.screen.get_width() - total_width) // 2
        base_y = self.screen.get_height() - (card_height // 2)

        for i, card in enumerate(hand):
            x = start_x + i * (card_width + card_spacing)
            card_rect = pygame.Rect(x, base_y, card_width, card_height // 2 + 20)
            if card_rect.collidepoint(pos):
                return i
        return None

    def player_turn(self, selected_card_index):
        selected_card = self.player.play_card(selected_card_index)

        if selected_card.suit == 'Hearts':
            actions = [
                {'text': f"Attack ({selected_card.get_attack_value()})", 'value': 'Attack'},
                {'text': f"Heal ({selected_card.get_attack_value()})", 'value': 'Heal'}
            ]
            self.selected_action = None
            self.get_player_action(actions, selected_card)
        elif selected_card.suit == 'Clubs':
            base_damage = selected_card.get_attack_value()
            damage = base_damage * 2  # Double the damage for Clubs
            self.ai_player.receive_damage(damage)
            message = f"You attacked for {damage} damage with Clubs (double damage)!"
            self.display_message(message)
            # Discard the card
            self.deck.discard(selected_card)
            # Check if player's hand is empty
            if len(self.player.hand) == 0:
                self.player.draw_cards(self.deck, 1)  # Only draw one card
                self.display_message("Your hand was empty! Drawing 1 new card.")
            # End of player's turn
            self.current_turn = 'AI'
        elif selected_card.suit == 'Diamonds':
            actions = [
                {'text': f"Attack ({selected_card.get_attack_value()})", 'value': 'Attack'},
                {'text': "Defense", 'value': 'Defense'}
            ]
            self.selected_action = None
            self.get_player_action(actions, selected_card)
        elif selected_card.suit == 'Spades':
            if len(self.player.hand) == 0:
                self.display_message("No cards to combine with Spades.")
                self.player.hand.append(selected_card)
                return
            else:
                self.waiting_for_second_card = True
                self.message = "Select a card to combine with Spades."
                self.selected_second_card_index = None
                self.wait_for_second_card(selected_card)
                return
        elif selected_card.value == 'Ace':
            damage = 1
            self.ai_player.receive_damage(damage)
            message = f"You dealt {damage} damage with an Ace!"
            self.display_message(message)
            max_hand_limit = 5
            cards_needed = max_hand_limit - len(self.player.hand)
            if cards_needed > 0:
                self.player.draw_cards(self.deck, cards_needed)
                self.display_message(f"You refilled your hand to {max_hand_limit} cards!")
            self.deck.discard(selected_card)
            if len(self.player.hand) == 0:
                self.player.draw_cards(self.deck, 5)
                self.display_message("Your hand was empty! Drawing 5 new cards.")
            self.current_turn = 'AI'
        else:
            damage = selected_card.get_attack_value()
            self.ai_player.receive_damage(damage)
            message = f"You attacked for {damage} damage!"
            self.display_message(message)
            self.deck.discard(selected_card)
            if len(self.player.hand) == 0:
                self.player.draw_cards(self.deck, 5)
                self.display_message("Your hand was empty! Drawing 5 new cards.")
            self.current_turn = 'AI'

    def get_player_action(self, actions, selected_card):
        self.create_action_buttons(actions)
        self.selected_action = None
        waiting_for_action = True
        while waiting_for_action and self.running:
            self.handle_events()
            self.render()
            if self.selected_action:
                action_value = self.selected_action
                if action_value == 'Attack':
                    damage = selected_card.get_attack_value()
                    self.ai_player.receive_damage(damage)
                    message = f"You attacked for {damage} damage!"
                    self.display_message(message)
                elif action_value == 'Heal':
                    top_card = self.player.top_cards[self.player.current_top_card_index]
                    heal_amount = selected_card.get_attack_value()
                    top_card['health'] = min(top_card['health'] + heal_amount, top_card['max_health'])
                    message = f"You healed your {top_card['name']} for {heal_amount} health!"
                    self.display_message(message)
                elif action_value == 'Defense':
                    self.player.defense_active = True
                    self.display_message("You have activated defense!")
                self.deck.discard(selected_card)
                if len(self.player.hand) == 0:
                    self.player.draw_cards(self.deck, 5)
                    self.display_message("Your hand was empty! Drawing 5 new cards.")
                self.current_turn = 'AI'
                self.action_buttons.clear()
                waiting_for_action = False
            self.clock.tick(60)

    def create_action_buttons(self, actions):
        self.action_buttons = []
        button_width = 200
        button_height = 50
        spacing = 20
        total_width = len(actions) * button_width + (len(actions) - 1) * spacing
        start_x = (self.screen.get_width() - total_width) // 2
        y = self.screen.get_height() - button_height - 100

        for i, action in enumerate(actions):
            x = start_x + i * (button_width + spacing)
            button = Button(
                text=action['text'],
                x=x,
                y=y,
                width=button_width,
                height=button_height,
                font=self.font,
                callback=self.handle_action_selection,
                args=[action['value']]
            )
            self.action_buttons.append(button)

    def handle_action_selection(self, action_value):
        self.selected_action = action_value

    def wait_for_second_card(self, spades_card):
        self.waiting_for_second_card = True
        while self.waiting_for_second_card and self.running:
            self.handle_events()
            self.render()
            if self.selected_second_card_index is not None:
                second_card = self.player.hand.pop(self.selected_second_card_index)
                total_damage = spades_card.get_attack_value() + second_card.get_attack_value()
                self.ai_player.receive_damage(total_damage)
                message = f"You attacked for {total_damage} damage with Spades combo!"
                self.display_message(message)
                self.deck.discard(spades_card)
                self.deck.discard(second_card)
                if len(self.player.hand) == 0:
                    self.player.draw_cards(self.deck, 5)
                    self.display_message("Your hand was empty! Drawing 5 new cards.")
                self.current_turn = 'AI'
                self.waiting_for_second_card = False
                self.selected_second_card_index = None
                self.action_buttons.clear()
            self.clock.tick(60)

    def display_message(self, message):
        self.message = message
        print(message)
        if not self.waiting_for_second_card:
            self.add_action_to_history(message)

    def draw_message(self):
        if self.message:
            text_surface = self.font.render(self.message, True, (255, 255, 255))
            x = (self.screen.get_width() - text_surface.get_width()) // 2
            if self.waiting_for_second_card:
                y = self.screen.get_height() - 250
            else:
                y = 20
            self.screen.blit(text_surface, (x, y))

    def ai_turn(self):
        # Pass the player's current top card to the AI's decide_action method
        player_top_card = self.player.top_cards[self.player.current_top_card_index]
        selected_card = self.ai_player.decide_action(player_top_card)
        if selected_card is None:
            self.display_message("AI has no cards to play.")
            self.current_turn = 'Player'
            return

        if selected_card.suit == 'Hearts':
            action = random.choice(['Attack', 'Heal'])
            if action == 'Attack':
                damage = selected_card.get_attack_value()
                damage = self.apply_defense(damage)
                self.player.receive_damage(damage)
                message = f"AI attacked you for {damage} damage!"
                self.display_message(message)
            elif action == 'Heal':
                top_card = self.ai_player.top_cards[self.ai_player.current_top_card_index]
                heal_amount = selected_card.get_attack_value()
                top_card['health'] = min(top_card['health'] + heal_amount, top_card['max_health'])
                message = f"AI healed its {top_card['name']} for {heal_amount} health!"
                self.display_message(message)
        elif selected_card.suit == 'Clubs':
            base_damage = selected_card.get_attack_value()
            damage = base_damage * 2  # Double the damage for Clubs
            damage = selected_card.get_attack_value()
            damage = self.apply_defense(damage)
            self.player.receive_damage(damage)
            message = f"AI attacked you for {damage} damage ({base_damage} x2) with Clubs!"
            self.display_message(message)
        elif selected_card.suit == 'Diamonds':
            action = random.choice(['Attack', 'Defense'])
            if action == 'Attack':
                damage = selected_card.get_attack_value()
                damage = self.apply_defense(damage)
                self.player.receive_damage(damage)
                message = f"AI attacked you for {damage} damage!"
                self.display_message(message)
            elif action == 'Defense':
                self.ai_player.defense_active = True
                self.display_message("AI has activated defense!")
        elif selected_card.suit == 'Spades':
            if len(self.ai_player.hand) == 0:
                damage = selected_card.get_attack_value()
                damage = self.apply_defense(damage)
                self.player.receive_damage(damage)
                message = f"AI attacked you for {damage} damage with Spades!"
                self.display_message(message)
            else:
                second_card = self.ai_player.play_card(0)
                total_damage = selected_card.get_attack_value() + second_card.get_attack_value()
                total_damage = self.apply_defense(total_damage)
                self.player.receive_damage(total_damage)
                message = f"AI attacked you for {total_damage} damage with Spades combo!"
                self.display_message(message)
                self.deck.discard(second_card)
        elif selected_card.value == 'Ace':
            damage = 1
            damage = self.apply_defense(damage)
            self.player.receive_damage(damage)
            message = f"AI dealt {damage} damage with an Ace!"
            self.display_message(message)
            max_hand_limit = 5
            cards_needed = max_hand_limit - len(self.ai_player.hand)
            if cards_needed > 0:
                self.ai_player.draw_cards(self.deck, cards_needed)
                self.display_message("AI refilled its hand!")
        else:
            damage = selected_card.get_attack_value()
            damage = self.apply_defense(damage)
            self.player.receive_damage(damage)
            message = f"AI attacked you for {damage} damage!"
            self.display_message(message)

        self.deck.discard(selected_card)
        if len(self.ai_player.hand) == 0:
            self.ai_player.draw_cards(self.deck, 5)
            self.display_message("AI's hand was empty! AI draws 5 new cards.")
        if self.ai_player.defense_active:
            self.ai_player.defense_active = False
        self.current_turn = 'Player'

    def apply_defense(self, damage):
        if self.player.defense_active:
            damage = damage // 2
            self.player.defense_active = False
        return damage
