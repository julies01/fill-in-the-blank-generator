import pygame
from constants import WHITE, BLUE, DARK_GRAY

"""
TextInputBox class for handling multi-line text input with word wrapping, scrolling, and cursor management.
"""
class TextInputBox:
    """
    Initializes the TextInputBox with position, size, font, and other properties.
    Args:        x (int): The x-coordinate of the top-left corner of the input box.
        y (int): The y-coordinate of the top-left corner of the input box.
        w (int): The width of the input box.
        h (int): The height of the input box.
        font (pygame.font.Font): The font used for rendering text.
        text (str, optional): The initial text in the input box. Defaults to ''.    max_chars (int, optional): 
        The maximum number of characters allowed in the input box. Defaults to 10000.
    """
    def __init__(self, x, y, w, h, font, text='', max_chars=10000):
        """
        Initializes the TextInputBox with position, size, font, and other properties.
        Args:
            x (int): The x-coordinate of the top-left corner of the input box.
            y (int): The y-coordinate of the top-left corner of the input box.
            w (int): The width of the input box.
            h (int): The height of the input box.
            font (pygame.font.Font): The font used for rendering text.
            text (str, optional): The initial text in the input box. Defaults to ''.
            max_chars (int, optional): The maximum number of characters allowed in the input box.
            Defaults to 10000.
        """
        self.rect = pygame.Rect(x, y, w, h)
        self.color = WHITE
        self.text = text
        self.font = font
        self.txt_surfaces = []
        self.visual_lines = []
        self.active = False
        self.cursor_pos = len(text)
        self.scroll = 0
        self.max_chars = max_chars
        self.line_spacing = 6
        self.scrollbar_width = 10
        self.scrollbar_dragging = False
        self.scrollbar_rect = pygame.Rect(
            self.rect.right - self.scrollbar_width - 4,
            self.rect.y + 4,
            self.scrollbar_width,
            self.rect.height - 8
        )
        self.update_surfaces()

    def handle_event(self, event):
        """
        Handles keyboard and mouse events for text input, cursor movement, and scrolling.
        Args:
            event (pygame.event.Event): The event to handle.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
                if self._scroll_handle_rect().collidepoint(event.pos):
                    self.scrollbar_dragging = True
                    return
                elif self.scrollbar_rect.collidepoint(event.pos):
                    handle = self._scroll_handle_rect()
                    if event.pos[1] < handle.y:
                        self.scroll = max(0, self.scroll - 1)
                    else:
                        self.scroll = min(self._max_scroll(), self.scroll + 1)
            else:
                self.active = False

        if event.type == pygame.MOUSEBUTTONUP:
            self.scrollbar_dragging = False
        elif event.type == pygame.MOUSEMOTION and self.scrollbar_dragging:
            max_scroll = self._max_scroll()
            if max_scroll > 0:
                handle = self._scroll_handle_rect()
                track_range = self.scrollbar_rect.height - handle.height
                rel_y = min(max(event.pos[1] - self.scrollbar_rect.y - handle.height // 2, 0), track_range)
                self.scroll = int((rel_y / track_range) * max_scroll) if track_range > 0 else 0

        if self.active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.text = self.text[:self.cursor_pos] + '\n' + self.text[self.cursor_pos:]
                    self.cursor_pos += 1
                elif event.key == pygame.K_BACKSPACE:
                    if self.cursor_pos > 0:
                        self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                        self.cursor_pos -= 1
                elif event.key == pygame.K_DELETE:
                    if self.cursor_pos < len(self.text):
                        self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
                elif event.key == pygame.K_LEFT:
                    if self.cursor_pos > 0:
                        self.cursor_pos -= 1
                elif event.key == pygame.K_RIGHT:
                    if self.cursor_pos < len(self.text):
                        self.cursor_pos += 1
                elif event.key == pygame.K_UP:
                    self.cursor_pos = self.move_cursor_vertically(-1)
                elif event.key == pygame.K_DOWN:
                    self.cursor_pos = self.move_cursor_vertically(1)
                elif (event.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_META or pygame.key.get_mods() & pygame.KMOD_CTRL)):
                    try:
                        import pyperclip
                        clip = pyperclip.paste()
                        if clip:
                            self.text = self.text[:self.cursor_pos] + clip + self.text[self.cursor_pos:]
                            self.cursor_pos += len(clip)
                    except ImportError:
                        pass
                elif (event.key == pygame.K_c and (pygame.key.get_mods() & pygame.KMOD_META or pygame.key.get_mods() & pygame.KMOD_CTRL)):
                    try:
                        import pyperclip
                        pyperclip.copy(self.text)
                    except ImportError:
                        pass
                elif event.unicode and len(self.text) < self.max_chars:
                    self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                    self.cursor_pos += len(event.unicode)

                self.update_surfaces()

    def _wrap_paragraph(self, paragraph):
        """
        Wraps a single paragraph of text into multiple lines based on the width of the input box.
        Args:
            paragraph (str): The paragraph to wrap.
            Returns:
                List[str]: A list of wrapped lines.
        """
        max_width = self.rect.width - 20
        if paragraph == "":
            return [""]
        words = paragraph.split(" ")
        lines = []
        current_line = ""

        for word in words:
            candidate = word if current_line == "" else current_line + " " + word
            if self.font.size(candidate)[0] <= max_width:
                current_line = candidate
            else:
                if current_line:
                    lines.append(current_line)
                if self.font.size(word)[0] <= max_width:
                    current_line = word
                else:
                    broken = ""
                    for char in word:
                        test = broken + char
                        if self.font.size(test)[0] <= max_width:
                            broken = test
                        else:
                            if broken:
                                lines.append(broken)
                            broken = char
                    current_line = broken

        if current_line:
            lines.append(current_line)
        return lines

    def update_surfaces(self):
        """
        Updates the rendered text surfaces based on the current text and wrapping.
        This method should be called whenever the text changes to ensure the display is updated correctly.
        """
        self.txt_surfaces = []
        self.visual_lines = []

        paragraphs = self.text.split('\n')
        for paragraph in paragraphs:
            wrapped = self._wrap_paragraph(paragraph)
            for line in wrapped:
                self.visual_lines.append(line)
                self.txt_surfaces.append(self.font.render(line, True, DARK_GRAY))

        if not self.visual_lines:
            self.visual_lines = [""]
            self.txt_surfaces = [self.font.render("", True, DARK_GRAY)]

    def _cursor_visual_position(self):
        """
        Calculates the visual line index and column position of the cursor based on the current text and cursor position.
        Returns:
            Tuple[int, int]: A tuple containing the visual line index and column position of the cursor
        """
        paragraphs = self.text.split('\n')
        text_before = self.text[:self.cursor_pos]

        visual_line_index = 0
        running_pos = 0

        for paragraph in paragraphs:
            wrapped = self._wrap_paragraph(paragraph)
            paragraph_text = paragraph
            paragraph_length = len(paragraph_text)

            if running_pos + paragraph_length >= len(text_before):
                local_pos = len(text_before) - running_pos
                consumed = 0
                for line in wrapped:
                    line_len = len(line)
                    if local_pos <= line_len:
                        return visual_line_index, local_pos
                    local_pos -= line_len
                    consumed += 1
                    visual_line_index += 1
                return visual_line_index, 0

            visual_line_index += len(wrapped)
            running_pos += paragraph_length + 1

        return len(self.visual_lines) - 1, len(self.visual_lines[-1])

    def get_cursor_line_col(self):
        """
        Returns the visual line index and column position of the cursor.
        Returns:
            Tuple[int, int]: A tuple containing the visual line index and column position of the cursor
        """
        return self._cursor_visual_position()

    def move_cursor_vertically(self, direction):
        """
        Moves the cursor up or down by one visual line, maintaining the horizontal position as much as possible.
        Args:
            direction (int): The direction to move the cursor (-1 for up, 1 for down).
            Returns: 
            int: The new cursor position after moving vertically.
        """
        line_idx, col = self.get_cursor_line_col()
        new_line_idx = max(0, min(len(self.visual_lines) - 1, line_idx + direction))
        new_col = min(len(self.visual_lines[new_line_idx]), col)

        pos = 0
        for i in range(new_line_idx):
            pos += len(self.visual_lines[i]) + 1
        return min(pos + new_col, len(self.text))

    def _max_scroll(self):
        """
        Calculates the maximum scroll value based on the total number of visual lines and the number of lines that can be displayed at once.
        Returns:
            int: The maximum scroll value.
        """
        visible_lines = max(1, (self.rect.height - 16) // (self.font.get_height() + self.line_spacing))
        total_lines = len(self.txt_surfaces) if hasattr(self, "txt_surfaces") else len(self.words)
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

    def draw(self, screen):
        """
        Draws the text input box on the screen, including the text, cursor, and scrollbar if needed.
        Args:
            screen (pygame.Surface): The surface to draw on.
        """
        pygame.draw.rect(screen, self.color, self.rect, 0, border_radius=6)
        pygame.draw.rect(screen, BLUE, self.rect, 2, border_radius=6)

        old_clip = screen.get_clip()
        screen.set_clip(self.rect)

        line_height = self.font.get_height() + self.line_spacing
        visible_lines = (self.rect.height - 16) // line_height

        for line_idx, surf in enumerate(self.txt_surfaces):
            if line_idx < self.scroll or line_idx >= self.scroll + visible_lines:
                continue

            y = self.rect.y + 8 + (line_idx - self.scroll) * line_height
            screen.blit(surf, (self.rect.x + 10, y))

        if self.active:
            line_idx, col = self.get_cursor_line_col()
            if self.scroll <= line_idx < self.scroll + visible_lines:
                line_text = self.visual_lines[line_idx]
                cursor_x = self.rect.x + 10 + self.font.size(line_text[:col])[0]
                cursor_y = self.rect.y + 8 + (line_idx - self.scroll) * line_height
                pygame.draw.line(screen, BLUE, (cursor_x, cursor_y), (cursor_x, cursor_y + self.font.get_height()), 2)

        if self._max_scroll() > 0:
            pygame.draw.rect(screen, (210, 210, 210), self.scrollbar_rect, border_radius=5)
            pygame.draw.rect(screen, (130, 130, 130), self._scroll_handle_rect(), border_radius=5)

        screen.set_clip(old_clip)
