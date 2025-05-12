import pygame
import sys
import random
import re

# Colors
WHITE = (255, 255, 255)
BLUE = (52, 120, 246)
LIGHT_GRAY = (230, 230, 230)
DARK_GRAY = (100, 100, 100)

# Window settings
pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('Fill in the Blank Generator')
clock = pygame.time.Clock()

font = pygame.font.SysFont('Arial', int(HEIGHT * 0.04))

class TextInputBox:
    def __init__(self, x, y, w, h, font, text='', max_chars=10000):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = WHITE  # Always white
        self.text = text
        self.font = font
        self.txt_surfaces = []
        self.active = False
        self.cursor_pos = len(text)
        self.scroll = 0
        self.max_chars = max_chars
        self.line_spacing = 6
        self.update_surfaces()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
        if self.active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.text = self.text[:self.cursor_pos] + '\n' + self.text[self.cursor_pos:]
                    self.cursor_pos += 1
                elif event.key == pygame.K_BACKSPACE:
                    if self.cursor_pos > 0:
                        self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                        self.cursor_pos -= 1
                elif event.key == pygame.K_DELETE:
                    if self.cursor_pos < len(self.text):
                        self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.scroll = max(0, self.scroll - 1)
                elif event.button == 5:
                    self.scroll += 1

    def move_cursor_vertically(self, direction):
        # Move cursor up or down a line
        lines = self.text.split('\n')
        line_idx, col = self.get_cursor_line_col()
        new_line_idx = max(0, min(len(lines)-1, line_idx + direction))
        new_col = min(len(lines[new_line_idx]), col)
        # Calculate new cursor_pos
        pos = sum(len(l)+1 for l in lines[:new_line_idx]) + new_col
        return pos

    def get_cursor_line_col(self):
        lines = self.text.split('\n')
        pos = 0
        for i, line in enumerate(lines):
            if self.cursor_pos <= pos + len(line):
                return i, self.cursor_pos - pos
            pos += len(line) + 1
        return len(lines)-1, len(lines[-1])

    def update_surfaces(self):
        self.txt_surfaces = []
        lines = self.text.split('\n')
        for line in lines:
            self.txt_surfaces.append(self.font.render(line, True, DARK_GRAY))

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 0, border_radius=6)
        pygame.draw.rect(screen, BLUE, self.rect, 2, border_radius=6)
        # Draw text
        y = self.rect.y + 8
        visible_lines = (self.rect.height - 16) // (self.font.get_height() + self.line_spacing)
        for i, surf in enumerate(self.txt_surfaces[self.scroll:self.scroll+visible_lines]):
            screen.blit(surf, (self.rect.x + 10, y))
            y += self.font.get_height() + self.line_spacing
        # Draw cursor if active
        if self.active:
            line_idx, col = self.get_cursor_line_col()
            if self.scroll <= line_idx < self.scroll + visible_lines:
                cursor_x = self.rect.x + 10 + self.font.size(self.text.split('\n')[line_idx][:col])[0]
                cursor_y = self.rect.y + 8 + (line_idx - self.scroll) * (self.font.get_height() + self.line_spacing)
                pygame.draw.line(screen, BLUE, (cursor_x, cursor_y), (cursor_x, cursor_y + self.font.get_height()), 2)

class Slider:
    def __init__(self, x, y, w, min_val, max_val, start_val):
        self.rect = pygame.Rect(x, y, w, int(HEIGHT * 0.035))
        self.min_val = min_val
        self.max_val = max_val
        self.value = start_val
        self.handle_radius = int(self.rect.height // 2)
        self.handle_x = self.get_handle_x()
        self.dragging = False

    def get_handle_x(self):
        rel = (self.value - self.min_val) / (self.max_val - self.min_val)
        return int(self.rect.x + rel * (self.rect.width - 2 * self.handle_radius) + self.handle_radius)

    def handle_event(self, event):
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
        # Track
        pygame.draw.rect(screen, DARK_GRAY, (self.rect.x, self.rect.centery - 3, self.rect.width, 6), border_radius=3)
        # Handle
        self.handle_x = self.get_handle_x()
        pygame.draw.circle(screen, BLUE, (self.handle_x, self.rect.centery), self.handle_radius)
        pygame.draw.circle(screen, WHITE, (self.handle_x, self.rect.centery), self.handle_radius-4)
        # Value text
        percent_text = font.render(f'{self.value}%', True, DARK_GRAY)
        screen.blit(percent_text, (self.rect.right + 16, self.rect.centery - percent_text.get_height()//2))

class Button:
    def __init__(self, x, y, w, h, text, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.color = BLUE
        self.text_color = WHITE
        self.hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, screen):
        color = (52, 100, 200) if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=6)
        text_surf = self.font.render(self.text, True, self.text_color)
        screen.blit(text_surf, (self.rect.centerx - text_surf.get_width()//2, self.rect.centery - text_surf.get_height()//2))

class TextDisplay:
    def __init__(self, x, y, w, h, font):
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

    def set_text(self, text, hide_percentage):
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

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                self.scroll = max(0, self.scroll - 1)
            elif event.button == 5:  # Scroll down
                self.scroll += 1
            elif event.button == 1:  # Left click
                current_time = pygame.time.get_ticks()
                if current_time - self.last_click_time < self.double_click_threshold:
                    # Double click detected
                    mouse_pos = pygame.mouse.get_pos()
                    if self.rect.collidepoint(mouse_pos):
                        # Find clicked word
                        rel_x = mouse_pos[0] - self.rect.x
                        rel_y = mouse_pos[1] - self.rect.y + self.scroll * (self.font.get_height() + self.line_spacing)
                        line_height = self.font.get_height() + self.line_spacing
                        line_idx = rel_y // line_height
                        
                        # Get the word at this position
                        current_x = 0
                        current_line = 0
                        for i, word in enumerate(self.words):
                            word_surf = self.font.render(word, True, DARK_GRAY)
                            if current_line == line_idx:
                                if current_x <= rel_x <= current_x + word_surf.get_width():
                                    if i in self.hidden_indices:
                                        self.revealed_indices.add(i)
                                    break
                            current_x += word_surf.get_width()
                            if word == '\n':
                                current_line += 1
                                current_x = 0
                
                self.last_click_time = current_time

    def reveal_all(self):
        self.revealed_indices = self.hidden_indices.copy()

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect, 0, border_radius=6)
        pygame.draw.rect(screen, BLUE, self.rect, 2, border_radius=6)
        
        x, y = self.rect.x + 10, self.rect.y + 8
        current_line = 0
        visible_lines = (self.rect.height - 16) // (self.font.get_height() + self.line_spacing)
        
        for i, word in enumerate(self.words):
            if current_line < self.scroll:
                if word == '\n':
                    current_line += 1
                continue
            if current_line >= self.scroll + visible_lines:
                break
                
            if i in self.hidden_indices and i not in self.revealed_indices:
                # Draw blank
                blank_width = self.font.size('_' * len(word))[0]
                pygame.draw.rect(screen, LIGHT_GRAY, (x, y, blank_width, self.font.get_height()))
                word_surf = self.font.render('_' * len(word), True, DARK_GRAY)
            else:
                word_surf = self.font.render(word, True, DARK_GRAY)
            
            screen.blit(word_surf, (x, y))
            x += word_surf.get_width()
            
            if word == '\n':
                x = self.rect.x + 10
                y += self.font.get_height() + self.line_spacing
                current_line += 1

# Add pyperclip to requirements.txt for clipboard support
# Usage: pip install pyperclip

# UI Elements (dynamic sizing)
margin = int(WIDTH * 0.07)
box_height = int(HEIGHT * 0.45)
input_box = TextInputBox(margin, int(HEIGHT * 0.13), WIDTH - 2 * margin, box_height, pygame.font.SysFont('Arial', int(HEIGHT * 0.03)))
slider_width = int(WIDTH * 0.7)
slider = Slider(margin, int(HEIGHT * 0.13) + box_height + int(HEIGHT * 0.05), slider_width, 0, 90, 30)
button_width = int(WIDTH * 0.12)
button_height = int(HEIGHT * 0.06)
generate_button = Button(margin + slider_width + int(WIDTH * 0.04), int(HEIGHT * 0.13) + box_height + int(HEIGHT * 0.05) - int(button_height/2) + int(HEIGHT*0.017), button_width, button_height, 'Generate', pygame.font.SysFont('Arial', int(HEIGHT * 0.03)))

# Second page elements
text_display = TextDisplay(margin, int(HEIGHT * 0.13), WIDTH - 2 * margin, box_height, pygame.font.SysFont('Arial', int(HEIGHT * 0.03)))
reveal_all_button = Button(margin, int(HEIGHT * 0.13) + box_height + int(HEIGHT * 0.05), button_width, button_height, 'Reveal All', pygame.font.SysFont('Arial', int(HEIGHT * 0.03)))
back_button = Button(WIDTH - margin - button_width, int(HEIGHT * 0.13) + box_height + int(HEIGHT * 0.05), button_width, button_height, 'Back', pygame.font.SysFont('Arial', int(HEIGHT * 0.03)))

# Add window control buttons
window_control_size = int(HEIGHT * 0.03)
window_control_spacing = int(HEIGHT * 0.01)
close_button = Button(window_control_spacing, window_control_spacing, window_control_size, window_control_size, '×', pygame.font.SysFont('Arial', int(HEIGHT * 0.025)))
full_button = Button(window_control_spacing + window_control_size + window_control_spacing, window_control_spacing, window_control_size, window_control_size, '□', pygame.font.SysFont('Arial', int(HEIGHT * 0.025)))
small_button = Button(window_control_spacing + (window_control_size + window_control_spacing) * 2, window_control_spacing, window_control_size, window_control_size, '−', pygame.font.SysFont('Arial', int(HEIGHT * 0.025)))

# Add window state
is_fullscreen = True
is_minimized = False
original_size = (WIDTH, HEIGHT)

def toggle_fullscreen():
    global screen, is_fullscreen, WIDTH, HEIGHT
    is_fullscreen = not is_fullscreen
    if is_fullscreen:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))

def minimize_window():
    global screen, is_minimized, WIDTH, HEIGHT
    is_minimized = not is_minimized
    if is_minimized:
        screen = pygame.display.set_mode((WIDTH, int(HEIGHT * 0.1)))
    else:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))

# State
current_page = "input"  # "input" or "result"

def redraw():
    # Background
    screen.fill(LIGHT_GRAY)
    
    # Draw window control buttons
    close_button.draw(screen)
    full_button.draw(screen)
    small_button.draw(screen)
    
    if current_page == "input":
        # Title
        title_surface = font.render('Fill in the Blank Generator', True, BLUE)
        screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, int(HEIGHT * 0.04)))
        # Draw input box
        input_box.draw(screen)
        # Draw slider
        slider.draw(screen)
        # Draw button
        generate_button.draw(screen)
    else:  # result page
        # Title
        title_surface = font.render('Fill in the Blanks', True, BLUE)
        screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, int(HEIGHT * 0.04)))
        # Draw text display
        text_display.draw(screen)
        # Draw buttons
        reveal_all_button.draw(screen)
        back_button.draw(screen)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and not (pygame.key.get_mods() & pygame.KMOD_ALT):
                running = False
            
        # Handle window control buttons
        if close_button.handle_event(event):
            running = False
        if full_button.handle_event(event):
            toggle_fullscreen()
        if small_button.handle_event(event):
            minimize_window()
            
        if current_page == "input":
            input_box.handle_event(event)
            slider.handle_event(event)
            if generate_button.handle_event(event):
                text_display.set_text(input_box.text, slider.value)
                current_page = "result"
        else:  # result page
            text_display.handle_event(event)
            if reveal_all_button.handle_event(event):
                text_display.reveal_all()
            if back_button.handle_event(event):
                current_page = "input"

    redraw()
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit() 