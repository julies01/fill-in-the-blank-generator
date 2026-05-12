import pygame
from constants import WHITE, BLUE

"""
Defines a Button class for creating interactive buttons in the Pygame application.
The Button class includes methods for handling mouse events and drawing the button on the screen.
"""
class Button:
    """
    A class representing a clickable button in the Pygame application.
    Attributes:
        rect (pygame.Rect): The rectangle defining the button's position and size.
        text (str): The text displayed on the button.
        font (pygame.font.Font): The font used to render the button's text.
        color (tuple): The background color of the button.
        text_color (tuple): The color of the button's text.
        hovered (bool): A flag indicating whether the mouse is currently hovering over the button.
        """
    def __init__(self, x, y, w, h, text, font):
        """
        Initializes the Button with the given parameters.
        Args:
            x (int): The x-coordinate of the button's top-left corner.
            y (int): The y-coordinate of the button's top-left corner.
            w (int): The width of the button.
            h (int): The height of the button.
            text (str): The text displayed on the button.
            font (pygame.font.Font): The font used to render the button's text.
        """
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.color = BLUE
        self.text_color = WHITE
        self.hovered = False

    def handle_event(self, event):
        """
        Handles mouse events for the button, allowing it to respond to clicks and hover states.
        Args:            
            event (pygame.event.Event): The event to handle.
        Returns:
            bool: True if the button was clicked, False otherwise.
        """
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, screen):
        """
        Draws the button on the screen, changing its appearance based on whether it is hovered.
        Args:
            screen (pygame.Surface): The surface to draw on.
        """
        color = (52, 100, 200) if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=6)
        text_surf = self.font.render(self.text, True, self.text_color)
        screen.blit(text_surf, (self.rect.centerx - text_surf.get_width()//2, self.rect.centery - text_surf.get_height()//2))
