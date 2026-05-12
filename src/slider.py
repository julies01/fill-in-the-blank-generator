import pygame
from constants import DARK_GRAY, BLUE, WHITE

class Slider:
    def __init__(self, x, y, w, min_val, max_val, start_val, window_height, font):
        """
        Initializes the slider with the given parameters.
        Args:
            x (int): The x-coordinate of the slider's top-left corner.
            y (int): The y-coordinate of the slider's top-left corner.
            w (int): The width of the slider.
            min_val (int): The minimum value of the slider.
            max_val (int): The maximum value of the slider.
            start_val (int): The initial value of the slider.
            window_height (int): The height of the window, used to determine the slider's height
            font (pygame.font.Font): The font used to render the slider's value text.
        """
        self.rect = pygame.Rect(x, y, w, int(window_height * 0.035))
        self.min_val = min_val
        self.max_val = max_val
        self.value = start_val
        self.handle_radius = int(self.rect.height // 2)
        self.handle_x = self.get_handle_x()
        self.dragging = False
        self.font = font

    def get_handle_x(self):
        """
        Calculates the x-coordinate of the slider handle based on the current value.
        Returns:
            int: The x-coordinate of the slider handle.
        """
        rel = (self.value - self.min_val) / (self.max_val - self.min_val)
        return int(self.rect.x + rel * (self.rect.width - 2 * self.handle_radius) + self.handle_radius)

    def handle_event(self, event):
        """
        Handles mouse events for the slider, allowing the user to click and drag the handle to change the value.
        Args:
            event (pygame.event.Event): The event to handle.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.Rect(self.handle_x - self.handle_radius, self.rect.centery - self.handle_radius, self.handle_radius*2, self.handle_radius*2).collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            x = min(max(event.pos[0], self.rect.x + self.handle_radius), self.rect.x + self.rect.width - self.handle_radius)
            rel = (x - self.rect.x - self.handle_radius) / (self.rect.width - 2 * self.handle_radius)
            self.value = int(self.min_val + rel * (self.max_val - self.min_val))
            self.handle_x = self.get_handle_x()

    def draw(self, screen):
        """
        Draws the slider on the screen, including the track, handle, and current value.
        Args:
            screen (pygame.Surface): The surface to draw on.
        """
        # Track
        pygame.draw.rect(screen, DARK_GRAY, (self.rect.x, self.rect.centery - 3, self.rect.width, 6), border_radius=3)
        # Handle
        self.handle_x = self.get_handle_x()
        pygame.draw.circle(screen, BLUE, (self.handle_x, self.rect.centery), self.handle_radius)
        pygame.draw.circle(screen, WHITE, (self.handle_x, self.rect.centery), self.handle_radius-4)
        # Value text
        percent_text = self.font.render(f'{self.value}%', True, DARK_GRAY)
        screen.blit(percent_text, (self.rect.right + 16, self.rect.centery - percent_text.get_height()//2))