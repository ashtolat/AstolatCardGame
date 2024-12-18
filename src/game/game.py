# src/game/game.py

import pygame
import os
import random
from deck import Deck
from player import Player
from ai_player import AIPlayer
from utils import get_card
from button import Button

MAX_HAND_SIZE = 5  # Define the maximum hand size


class Game:
    # Initializes the game, loads assets, and sets up initial game state.
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
        self.history_font = pygame.font.Font(os.path.join(assets_path, 'font.ttf'), 16)  # Smaller font for history
        self.background = pygame.image.load(
            os.path.join(assets_path, 'background.png')).convert()
        self.clock = pygame.time.Clock()
        self.message = ""
        self.defense_active = False

        self.hand_message_printed = False  # Flag to ensure hand is printed only once per turn

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

    # Retrieves the path to the game's assets directory.
    def get_assets_path(self):
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, 'assets')

    # Creates the buttons for the player's Jesters to refresh their hand.
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

    # Toggles the visibility of the AI's hand on the screen.
    def toggle_show_ai_cards(self):
        self.show_ai_cards = not self.show_ai_cards
        if self.show_ai_cards:
            self.show_ai_cards_button.text = "Hide AI cards"
        else:
            self.show_ai_cards_button.text = "Show AI cards"

    # Ends the game and returns to the main menu.
    def back_to_menu(self):
        self.running = False

    # Allows the player to use a Jester to refresh their hand.
    def use_player_jester(self, index):
        if self.player_jesters > 0:
            # Discard all current hand cards
            for card in self.player.hand:
                self.deck.discard(card)
            self.player.hand.clear()
            # Draw 5 new cards
            self.player.draw_cards(self.deck, 5)
            self.display_message("You have refreshed your hand using a Jester!")
            self.player_jesters -= 1
            self.create_player_jester_buttons()
            self.current_turn = 'AI'

    # Starts the game and initializes both players' hands.
    def start_game(self):
        self.player.draw_cards(self.deck, 5)
        self.ai_player.draw_cards(self.deck, 5)
        self.game_loop()

    # Main game loop: processes events, updates game state, and renders frames.
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

    # Begins the player's turn by refilling their hand and logging it.
    def start_player_turn(self):
        # Refill player's hand to MAX_HAND_SIZE
        self.player.draw_cards(self.deck, MAX_HAND_SIZE - len(self.player.hand))
        
        # Log the player's hand to the command line once
        if not self.hand_message_printed:
            self.hand_message("Player", self.player.hand)
            self.hand_message_printed = True

        # Set the turn to Player
        self.current_turn = 'Player'

    # Begins the AI's turn by refilling its hand and executing its action.
    def start_ai_turn(self):
        # Refill AI's hand to MAX_HAND_SIZE
        self.ai_player.draw_cards(self.deck, MAX_HAND_SIZE - len(self.ai_player.hand))
        
        # Log the AI's hand to the command line once
        if self.hand_message_printed:
            self.hand_message("AI", self.ai_player.hand)
            self.hand_message_printed = False

        # Execute the AI's turn
        self.ai_turn()
    
    # Ends the current turn and transitions to the next turn.
    def end_turn(self):
        self.hand_message_printed = False  # Reset for the next turn
        if self.current_turn == 'Player':
            self.current_turn = 'AI'
            self.start_ai_turn()
        else:
            self.current_turn = 'Player'
            self.start_player_turn()

    # Prints the player's or AI's current hand to the console.
    def hand_message(self, player_name, hand):
        hand_description = ', '.join([f"{card.value} of {card.suit}" for card in hand])
        print(f"{player_name}'s Hand: [{hand_description}]")

    # Handles player input and UI interactions during the game.
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

    # Checks for win/lose conditions and updates the game state.
    def update_game_state(self):
        # Only check for game over conditions if the game isn't already over
        if not self.game_over:
            if self.player.is_defeated():
                self.display_end_message("You have been defeated!")
                self.game_over = True
            elif self.ai_player.is_defeated():
                self.display_end_message("You have won the game!")
                self.game_over = True

    # Renders the game elements (e.g., cards, buttons, background) on the screen.
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

    # Displays the game over screen when the game ends.
    def draw_game_over_screen(self):
        self.screen.fill((0, 0, 0))
        message_surface = self.font.render(self.message, True, (255, 255, 255))
        message_rect = message_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(message_surface, message_rect)
        self.back_to_menu_button.draw(self.screen)

    # Draws the AI's remaining Jesters on the screen.
    def draw_ai_jesters(self):
        x = 10
        y = 10
        for i in range(self.ai_jesters):
            self.screen.blit(self.ai_jester_image,
                             (x + i * (self.ai_jester_image.get_width() + 10), y))

    # Displays the history of game actions on the screen.
    def draw_action_history(self):
        history_width = 280  # Reduced width to prevent overlap
        x = self.screen.get_width() - history_width - 10  # Positioned with some padding from the edge
        y = 50  # Positioned below the AI's mini cards
        line_height = 20  # Smaller line height
        max_width = history_width
        max_lines = (self.screen.get_height() - y - 10) // line_height

        displayed_lines = 0
        for entry in reversed(self.action_history[-15:]):
            wrapped_lines = self.wrap_text(entry, self.history_font, max_width)
            for line in wrapped_lines:
                if displayed_lines >= max_lines:
                    break
                text_surface = self.history_font.render(line, True, (255, 255, 255))
                self.screen.blit(text_surface, (x, y + displayed_lines * line_height))
                displayed_lines += 1
            if displayed_lines >= max_lines:
                break

    # Helper function to wrap long text for rendering.
    def wrap_text(self, text, font, max_width):
        """Helper function to wrap text for rendering."""
        words = text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
        return lines

    # Adds a message to the action history for display.
    def add_action_to_history(self, message):
        self.action_history.append(message)
        if len(self.action_history) > 15:
            self.action_history.pop(0)

    # Draws the player's hand of cards at the bottom of the screen.
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

    # Draws the AI's hand of cards at the top of the screen.
    def draw_ai_hand(self):
        if not self.ai_player.hand:
            return

        # Card positioning
        card_spacing = 20
        card_width = self.ai_player.hand[0].mini_image.get_width()
        card_height = self.ai_player.hand[0].mini_image.get_height()
        total_width = len(self.ai_player.hand) * card_width + (len(self.ai_player.hand) - 1) * card_spacing
        start_x = (self.screen.get_width() - total_width) // 2  # Center horizontally
        base_y = 10  # Top margin

        for i, card in enumerate(self.ai_player.hand):
            x = start_x + i * (card_width + card_spacing)
            if self.show_ai_cards:
                # Show actual AI cards if toggled on
                self.screen.blit(card.mini_image, (x, base_y))
            else:
                # Show card backs if AI cards are hidden
                self.screen.blit(self.mini_card_back_image, (x, base_y))

    # Displays the current top cards of both players and their health.
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

    # Draws a health bar for a card based on its current health.
    def draw_health_bar(self, x, y, current_health, max_health):
        bar_width = 100
        bar_height = 10
        fill = (current_health / max_health) * bar_width
        outline_rect = pygame.Rect(x, y, bar_width, bar_height)
        fill_rect = pygame.Rect(x, y, fill, bar_height)
        pygame.draw.rect(self.screen, (255, 0, 0), fill_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), outline_rect, 1)

    # Determines which card was clicked based on the mouse position.
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

    # Processes the player's action based on the selected card.
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
            damage = base_damage * 2  # Double damage for Clubs
            self.ai_player.receive_damage(damage)
            message = f"You attacked for {damage} damage with Clubs (double damage)!"
            self.display_message(message)
            self.deck.discard(selected_card)
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
            self.deck.discard(selected_card)
            self.current_turn = 'AI'
        else:
            damage = selected_card.get_attack_value()
            self.ai_player.receive_damage(damage)
            message = f"You attacked for {damage} damage!"
            self.display_message(message)
            self.deck.discard(selected_card)
            self.current_turn = 'AI'

    # Handles the player's decision-making for actions (attack, heal, etc)
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
                self.current_turn = 'AI'
                self.action_buttons.clear()
                waiting_for_action = False
            self.clock.tick(60)

    # Creates buttons for the player's action choices during their turn.
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

    # Processes the player's selected action (e.g., attack, heal, defend).
    def handle_action_selection(self, action_value):
        self.selected_action = action_value

    # Waits for the player to select a second card for a Spades combo.
    def wait_for_second_card(self, spades_card):
        self.waiting_for_second_card = True
        while self.waiting_for_second_card and self.running:
            self.handle_events()
            self.render()
            if self.selected_second_card_index is not None:
                second_card = self.player.play_card(self.selected_second_card_index)
                total_damage = spades_card.get_attack_value() + second_card.get_attack_value()
                self.ai_player.receive_damage(total_damage)
                message = f"You attacked for {total_damage} damage with Spades combo!"
                self.display_message(message)
                self.deck.discard(spades_card)
                self.deck.discard(second_card)
                self.current_turn = 'AI'
                self.waiting_for_second_card = False
                self.selected_second_card_index = None
                self.action_buttons.clear()
            self.clock.tick(60)

    # Displays a message on the screen and logs it in the history.
    def display_message(self, message):
        #self.message = message
        print(message)
        if not self.waiting_for_second_card:
            self.add_action_to_history(message)

    # Sets and displays the end-game message (win or lose)
    def display_end_message(self, message):
        self.message = message
        print(message)

    # Renders a message at the top of the screen during the game
    def draw_message(self):
        if self.message:
            text_surface = self.font.render(self.message, True, (255, 255, 255))
            x = (self.screen.get_width() - text_surface.get_width()) // 2
            if self.waiting_for_second_card:
                y = self.screen.get_height() - 200
            else:
                y = 20
            self.screen.blit(text_surface, (x, y))

    # Executes the AI's turn by deciding and performing one action.
    def ai_turn(self):
        # Get the player's current top card
        player_top_card = None
        if self.player.current_top_card_index < len(self.player.top_cards):
            player_top_card = self.player.top_cards[self.player.current_top_card_index]

        # AI decides which card to play
        selected_card = self.ai_player.decide_action(player_top_card, self.player.defense_active)

        # If AI uses a Jester to refresh its hand
        if selected_card == "Use Jester":
            if self.ai_player.jesters > 0:
                for card in self.ai_player.hand:
                    self.deck.discard(card)
                self.ai_player.hand.clear()
                self.ai_player.draw_cards(self.deck, 5)
                self.display_message("AI used a Jester to refresh its hand!")
                self.ai_player.jesters -= 1
            self.end_turn()  # End AI's turn after using Jester
            return

        # Handle the selected card or action
        if isinstance(selected_card, tuple):  # Spades combo
            spade, combo_card = selected_card
            self.execute_ai_attack(spade, combo_card)
        elif selected_card.suit == 'Hearts':
            # Heal the AI's top card
            top_card = self.ai_player.top_cards[self.ai_player.current_top_card_index]
            heal_amount = selected_card.get_attack_value()
            top_card['health'] = min(top_card['health'] + heal_amount, top_card['max_health'])
            self.display_message(f"AI healed its {top_card['name']} for {heal_amount} health!")
        elif selected_card.suit == 'Diamonds':
            # Activate defense
            self.ai_player.defense_active = True
            self.display_message("AI has activated defense!")
        else:
            # Default attack logic
            self.execute_ai_attack(selected_card)

        # Discard the selected card
        self.deck.discard(selected_card)

        # End AI's turn immediately after performing one action
        self.end_turn()
    
    # Executes the AI's chosen action based on the selected card.
    def execute_ai_action(self, card):
        if card.suit == 'Hearts':
            own_top_card = self.ai_player.top_cards[self.ai_player.current_top_card_index]
            if own_top_card['health'] < own_top_card['max_health'] / 2:
                heal_amount = card.get_attack_value()
                own_top_card['health'] = min(own_top_card['health'] + heal_amount, own_top_card['max_health'])
                self.display_message(f"AI healed its {own_top_card['name']} for {heal_amount} health!")
            else:
                self.execute_ai_attack(card)
        elif card.suit == 'Diamonds':
            self.ai_player.defense_active = True
            self.display_message("AI has activated defense!")
        else:
            self.execute_ai_attack(card)

    # Executes an AI attack, including combos, and applies damage.
    def execute_ai_attack(self, card, combo_card=None):
        damage = card.get_attack_value()
        if combo_card:
            damage += combo_card.get_attack_value()
            self.deck.discard(combo_card)

        if card.suit == 'Clubs':
            damage *= 2  # Double damage for Clubs

        # Apply player defense, if active
        damage = self.apply_defense(damage)

        self.player.receive_damage(damage)
        attack_message = f"AI attacked you for {damage} damage!"
        if combo_card:
            attack_message += f" (using {card.suit} + {combo_card.suit})"
        self.display_message(attack_message)

    # Applies the effects of defense cards and reduces damage
    def apply_defense(self, damage):
        if self.player.defense_active:
            damage = damage // 2
            self.player.defense_active = False
        elif self.ai_player.defense_active:
            damage = damage // 2
            self.ai_player.defense_active = False
        return damage