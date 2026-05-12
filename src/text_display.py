import pygame
import random
from constants import WHITE, BLUE, LIGHT_GRAY, DARK_GRAY



class TextDisplay:
    """
    A scrollable text display that shows the generated fill-in-the-blank text.
    It supports hiding a percentage of words, revealing them on double-click, and scrolling through the
    text if it exceeds the display area.
    Attributes:
        rect (pygame.Rect): The rectangle defining the position and size of the text display.
        font (pygame.font.Font): The font used to render the text.
        text (str): The full text to display.
        words (list): A list of words and whitespace characters in the text.
        hidden_indices (set): A set of indices of words that are currently hidden.
        revealed_indices (set): A set of indices of words that have been revealed by the user.
        scroll (int): The current scroll position (in lines).
        line_spacing (int): The vertical spacing between lines of text.
        last_click_time (int): The timestamp of the last mouse click, used for detecting double clicks.
        double_click_threshold (int): The maximum time (in milliseconds) between clicks to be considered a double click.
        scrollbar_width (int): The width of the scrollbar.
        scrollbar_dragging (bool): Whether the scrollbar is currently being dragged.
        scrollbar_rect (pygame.Rect): The rectangle defining the position and size of the scrollbar.
    """
    
    def __init__(self, x, y, w, h, font):
        """
        Initializes the TextDisplay with a position, size, and font.
        """
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.text = ""
        self.words = []
        self.hidden_indices = set()
        self.revealed_indices = set()
        self.scroll = 0
        self.line_spacing = 6
        self.last_click_time = 0
        self.double_click_threshold = 300  # milliseconds
        self.scrollbar_width = 10
        self.scrollbar_dragging = False
        self.scrollbar_rect = pygame.Rect(
            self.rect.right - self.scrollbar_width - 4,
            self.rect.y + 4,
            self.scrollbar_width,
            self.rect.height - 8
        )

    def set_text(self, text, hide_percentage):
        """
        Sets the text to display and randomly hides a percentage of the words.     
        Args:
            text (str): The text to display.
            hide_percentage (float): The percentage of words to hide.
        """
        self.text = text
        # Split text into words while preserving spaces, tabs, and newlines
        self.words = []
        current_word = ""
        for char in text:
            if char.isspace():
                if current_word:
                    self.words.append(current_word)
                    current_word = ""
                self.words.append(char)
            else:
                current_word += char
        if current_word:
            self.words.append(current_word)

        # Get indices of actual words (not spaces or newlines)
        word_indices = [i for i, word in enumerate(self.words) if not word.isspace()]
        # Calculate number of words to hide
        num_to_hide = int(len(word_indices) * (hide_percentage / 100))
        # Randomly select words to hide
        self.hidden_indices = set(random.sample(word_indices, num_to_hide))
        self.revealed_indices = set()
        self.scroll = 0

    def _layout_words(self):
        """
        Calculates the position of each word for rendering, taking into account line breaks and wrapping.
        Returns:
            list: A list of tuples containing (index, word, x, y, line_number) for each word.
        """
        max_width = self.rect.width - 20
        line_height = self.font.get_height() + self.line_spacing
        x = self.rect.x + 10
        y = self.rect.y + 8
        current_line = 0
        layout = []

        for i, word in enumerate(self.words):
            if word == '\n':
                current_line += 1
                x = self.rect.x + 10
                y += line_height
                layout.append((i, word, x, y, current_line))
                continue

            word_surf = self.font.render('_' * len(word), True, DARK_GRAY) if i in self.hidden_indices and i not in self.revealed_indices else self.font.render(word, True, DARK_GRAY)
            word_width = word_surf.get_width()

            if x > self.rect.x + 10 and x + word_width > self.rect.x + 10 + max_width:
                current_line += 1
                x = self.rect.x + 10
                y += line_height

            layout.append((i, word, x, y, current_line))
            x += word_width

        return layout

    def _total_visual_lines(self):
        """
        Calculates the total number of visual lines needed to display the text, based on the layout of words.    
        Returns:    
            int: The total number of visual lines.
        """
        layout = self._layout_words()
        if not layout:
            return 1
        return max(line for _, _, _, _, line in layout) + 1

    def handle_event(self, event):
        """
        Handles mouse events for scrolling and revealing words.
        Args:
            event (pygame.event.Event): The event to handle.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                self.scroll = max(0, self.scroll - 1)
            elif event.button == 5:  # Scroll down
                self.scroll = min(self._max_scroll(), self.scroll + 1)
            elif event.button == 1:
                if self._scroll_handle_rect().collidepoint(event.pos):
                    self.scrollbar_dragging = True
                    return
                if self.scrollbar_rect.collidepoint(event.pos):
                    handle = self._scroll_handle_rect()
                    if event.pos[1] < handle.y:
                        self.scroll = max(0, self.scroll - 1)
                    else:
                        self.scroll = min(self._max_scroll(), self.scroll + 1)
                # Left click on text area
                current_time = pygame.time.get_ticks()
                if current_time - self.last_click_time < self.double_click_threshold:
                    # Double click detected
                    mouse_pos = pygame.mouse.get_pos()
                    if self.rect.collidepoint(mouse_pos):
                        layout = self._layout_words()
                        rel_x = mouse_pos[0] - self.rect.x
                        rel_y = mouse_pos[1] - self.rect.y + self.scroll * (self.font.get_height() + self.line_spacing)
                        line_height = self.font.get_height() + self.line_spacing
                        line_idx = rel_y // line_height

                        for i, word, x, y, current_line in layout:
                            if current_line == line_idx:
                                word_surf = self.font.render('_' * len(word), True, DARK_GRAY) if i in self.hidden_indices and i not in self.revealed_indices else self.font.render(word, True, DARK_GRAY)
                                if x - (self.rect.x + 10) <= rel_x <= x - (self.rect.x + 10) + word_surf.get_width():
                                    if i in self.hidden_indices:
                                        self.revealed_indices.add(i)
                                    break
                
                self.last_click_time = current_time

        if event.type == pygame.MOUSEBUTTONUP:
            self.scrollbar_dragging = False
        elif event.type == pygame.MOUSEMOTION and self.scrollbar_dragging:
            max_scroll = self._max_scroll()
            if max_scroll > 0:
                handle = self._scroll_handle_rect()
                track_range = self.scrollbar_rect.height - handle.height
                rel_y = min(max(event.pos[1] - self.scrollbar_rect.y - handle.height // 2, 0), track_range)
                self.scroll = int((rel_y / track_range) * max_scroll) if track_range > 0 else 0
        self.scroll = max(0, min(self.scroll, self._max_scroll()))

    def reveal_all(self):
        """
        Reveals all hidden words.
        """
        self.revealed_indices = self.hidden_indices.copy()

    def draw(self, screen):
        """
        Draws the text display on the screen, including the text with hidden words as blanks and the scrollbar if needed.
        Args:
            screen (pygame.Surface): The surface to draw on.
        """
        pygame.draw.rect(screen, WHITE, self.rect, 0, border_radius=6)
        pygame.draw.rect(screen, BLUE, self.rect, 2, border_radius=6)

        old_clip = screen.get_clip()
        screen.set_clip(self.rect)
        
        line_height = self.font.get_height() + self.line_spacing
        visible_lines = (self.rect.height - 16) // line_height
        layout = self._layout_words()
        
        for i, word, x, y, current_line in layout:
            if current_line < self.scroll or current_line >= self.scroll + visible_lines:
                continue

            if word == '\n':
                continue

            render_y = self.rect.y + 8 + (current_line - self.scroll) * line_height

            if i in self.hidden_indices and i not in self.revealed_indices:
                blank_width = self.font.size('_' * len(word))[0]
                pygame.draw.rect(screen, LIGHT_GRAY, (x, render_y, blank_width, self.font.get_height()))
                word_surf = self.font.render('_' * len(word), True, DARK_GRAY)
            else:
                word_surf = self.font.render(word, True, DARK_GRAY)

            screen.blit(word_surf, (x, render_y))

        if self._max_scroll() > 0:
            pygame.draw.rect(screen, (210, 210, 210), self.scrollbar_rect, border_radius=5)
            pygame.draw.rect(screen, (130, 130, 130), self._scroll_handle_rect(), border_radius=5)

        screen.set_clip(old_clip)

    def _max_scroll(self):
        """
        Calculates the maximum scroll value based on the total number of visual lines and the number of lines that can be displayed at once.
        Returns:
            int: The maximum scroll value.
        """
        visible_lines = max(1, (self.rect.height - 16) // (self.font.get_height() + self.line_spacing))
        total_lines = self._total_visual_lines()
        return max(0, total_lines - visible_lines)

    def _scroll_handle_rect(self):
        """
        Calculates the rectangle for the scrollbar handle based on the current scroll position and the total scrollable range.
        Returns:
            pygame.Rect: The rectangle representing the scrollbar handle.
        """
        max_scroll = self._max_scroll()
        if max_scroll == 0:
            return pygame.Rect(self.scrollbar_rect.x, self.scrollbar_rect.y, self.scrollbar_rect.width, self.scrollbar_rect.height)

        visible_lines = max(1, (self.rect.height - 16) // (self.font.get_height() + self.line_spacing))
        handle_height = max(20, int(self.scrollbar_rect.height * visible_lines / (visible_lines + max_scroll)))
        handle_range = self.scrollbar_rect.height - handle_height
        handle_y = self.scrollbar_rect.y + int(handle_range * (self.scroll / max_scroll))
        return pygame.Rect(self.scrollbar_rect.x, handle_y, self.scrollbar_rect.width, handle_height)
