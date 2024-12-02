# src/game/menu.py

import pygame
import os
from game import Game

class Menu:
    def __init__(self, screen):
        self.screen = screen

        # Get the absolute path to the assets directory
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assets_path = os.path.join(base_path, 'assets')

        self.font = pygame.font.Font(os.path.join(self.assets_path, 'font.ttf'), 36)
        self.background = pygame.image.load(os.path.join(self.assets_path, 'background.png')).convert()
        self.clock = pygame.time.Clock()
        self.running = True

    def display_menu(self):
        while self.running:
            self.screen.blit(self.background, (0, 0))
            self.handle_events()
            self.render_menu()
            pygame.display.flip()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if self.start_rect.collidepoint(pos):
                    self.display_difficulty_selection()
                elif self.rules_rect.collidepoint(pos):
                    self.display_rules()
                elif self.exit_rect.collidepoint(pos):
                    self.running = False

    def render_menu(self):
        # Render menu options
        start_text = self.font.render("Start", True, (255, 255, 255))
        rules_text = self.font.render("Rules", True, (255, 255, 255))
        exit_text = self.font.render("Exit", True, (255, 255, 255))

        self.start_rect = start_text.get_rect(center=(self.screen.get_width()//2, 200))
        self.rules_rect = rules_text.get_rect(center=(self.screen.get_width()//2, 300))
        self.exit_rect = exit_text.get_rect(center=(self.screen.get_width()//2, 400))

        self.screen.blit(start_text, self.start_rect)
        self.screen.blit(rules_text, self.rules_rect)
        self.screen.blit(exit_text, self.exit_rect)

    def display_rules(self):
        # Display the rules screen
        showing_rules = True
        while showing_rules:
            self.screen.blit(self.background, (0, 0))
            rules_title = self.font.render("Game Rules", True, (255, 255, 255))
            back_text = self.font.render("Back", True, (255, 255, 255))

            rules_content = [
                "1. The game is played against an AI opponent.",
                "2. Each player starts with 5 cards.",
                "3. Defeat the opponent's top cards in order: Jack, Queen, King.",
                "5. Use cards to attack, heal, defend, or activate abilities.",
                "6. Hearts: Attack or heal based on card value.",
                "7. Diamonds: Attack or defend based on card value.",
                "8. Clubs: Attack with double damage.",
                "9. Spades: Combine with another card for a stronger attack.",
                "10. Jesters: Refresh your hand to 5 new cards.",
                "11. Win by defeating all of your opponent's top cards.",
            ]

            self.screen.blit(rules_title, (50, 50))
            for idx, line in enumerate(rules_content):
                rule_text = self.font.render(line, True, (255, 255, 255))
                self.screen.blit(rule_text, (50, 100 + idx * 40))

            back_rect = back_text.get_rect(topleft=(50, self.screen.get_height() - 100))
            self.screen.blit(back_text, back_rect)

            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    showing_rules = False
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if back_rect.collidepoint(pos):
                        showing_rules = False
            self.clock.tick(60)

    def display_difficulty_selection(self):
        selecting_difficulty = True
        while selecting_difficulty:
            self.screen.blit(self.background, (0, 0))
            # Render difficulty options
            easy_text = self.font.render("Easy", True, (255, 255, 255))
            medium_text = self.font.render("Medium", True, (255, 255, 255))
            hard_text = self.font.render("Hard", True, (255, 255, 255))

            easy_rect = easy_text.get_rect(center=(self.screen.get_width()//2, 200))
            medium_rect = medium_text.get_rect(center=(self.screen.get_width()//2, 300))
            hard_rect = hard_text.get_rect(center=(self.screen.get_width()//2, 400))

            self.screen.blit(easy_text, easy_rect)
            self.screen.blit(medium_text, medium_rect)
            self.screen.blit(hard_text, hard_rect)

            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    selecting_difficulty = False
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if easy_rect.collidepoint(pos):
                        game = Game(self.screen, 'Easy')
                        game.start_game()
                        selecting_difficulty = False
                    elif medium_rect.collidepoint(pos):
                        game = Game(self.screen, 'Medium')
                        game.start_game()
                        selecting_difficulty = False
                    elif hard_rect.collidepoint(pos):
                        game = Game(self.screen, 'Hard')
                        game.start_game()
                        selecting_difficulty = False
            self.clock.tick(60)
