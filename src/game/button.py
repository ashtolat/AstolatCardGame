# src/game/button.py

import pygame


class Button:
    def __init__(self, text=None, x=0, y=0, width=100, height=50, font=None, image=None, callback=None, args=None):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = font
        self.image = image
        self.callback = callback
        self.args = args or []

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.hovered = False

    def draw(self, screen):
        if self.image:
            # Draw the button
            screen.blit(self.image, (self.x, self.y))
        else:
            # rectangular button 
            pygame.draw.rect(screen, (200, 200, 200), self.rect)
            if self.hovered:
                pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
            else:
                pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)

            if self.text and self.font:
                text_surface = self.font.render(self.text, True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=self.rect.center)
                screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback(*self.args)
