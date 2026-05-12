import pygame, sys, random, re
from constants import WHITE, BLUE, LIGHT_GRAY, DARK_GRAY
from text_input_box import TextInputBox
from slider import Slider
from button import Button
from text_display import TextDisplay


# Window settings
pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('Fill in the Blank Generator')
clock = pygame.time.Clock()

font_path = font_path = "assets/fonts/Capriola-Regular.ttf"
font = pygame.font.Font(font_path, int(HEIGHT * 0.04))
small_font = pygame.font.Font(font_path, int(HEIGHT * 0.03))


margin = int(WIDTH * 0.07)
box_height = int(HEIGHT * 0.45)
input_box = TextInputBox(margin, int(HEIGHT * 0.13), WIDTH - 2 * margin, box_height, small_font)
slider_width = int(WIDTH * 0.7)
slider = Slider(margin, int(HEIGHT * 0.13) + box_height + int(HEIGHT * 0.05), slider_width, 0, 90, 30, HEIGHT, small_font)
button_width = int(WIDTH * 0.12)
button_height = int(HEIGHT * 0.06)
button_y = int(HEIGHT * 0.13) + box_height + int(HEIGHT * 0.05) + int(HEIGHT * 0.07)
clear_button = Button(margin, button_y, button_width, button_height, 'Clear', small_font)
generate_button = Button(WIDTH - margin - button_width, button_y, button_width, button_height, 'Generate', small_font)

# Second page elements
text_display = TextDisplay(margin, int(HEIGHT * 0.13), WIDTH - 2 * margin, box_height, small_font)
reveal_all_button = Button(margin, int(HEIGHT * 0.13) + box_height + int(HEIGHT * 0.05), button_width, button_height, 'Reveal All', small_font)
back_button = Button(WIDTH - margin - button_width, int(HEIGHT * 0.13) + box_height + int(HEIGHT * 0.05), button_width, button_height, 'Back', small_font)

# Add window control buttons
window_control_size = int(HEIGHT * 0.03)
window_control_spacing = int(HEIGHT * 0.01)
close_button = Button(window_control_spacing, window_control_spacing, window_control_size, window_control_size, '×', small_font)
full_button = Button(window_control_spacing + window_control_size + window_control_spacing, window_control_spacing, window_control_size, window_control_size, '', small_font)
small_button = Button(window_control_spacing + (window_control_size + window_control_spacing) * 2, window_control_spacing, window_control_size, window_control_size, '−', small_font)

# Add window state
is_fullscreen = True
is_minimized = False
original_size = (WIDTH, HEIGHT)

def toggle_fullscreen():
    """
    Toggles between fullscreen and windowed mode.
    """
    global screen, is_fullscreen, WIDTH, HEIGHT
    is_fullscreen = not is_fullscreen
    if is_fullscreen:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))

def minimize_window():
    """
    Minimizes the window.
    """
    global screen, is_minimized, WIDTH, HEIGHT
    is_minimized = not is_minimized
    if is_minimized:
        screen = pygame.display.set_mode((WIDTH, int(HEIGHT * 0.1)))
    else:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))

# State
current_page = "input"  # "input" or "result"

def redraw():
    """
    Redraws the entire screen based on the current state, including the background, 
    window controls, and page-specific elements.
    """
    # Background
    screen.fill(LIGHT_GRAY)
    
    # Draw window control buttons
    close_button.draw(screen)
    full_button.draw(screen)
    full_icon_size = max(6, window_control_size // 2)
    full_icon_rect = pygame.Rect(
        full_button.rect.centerx - full_icon_size // 2,
        full_button.rect.centery - full_icon_size // 2,
        full_icon_size,
        full_icon_size,
    )
    pygame.draw.rect(screen, WHITE, full_icon_rect, 2)
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
        clear_button.draw(screen)
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
            if clear_button.handle_event(event):
                input_box.text = ""
                input_box.cursor_pos = 0
                input_box.scroll = 0
                input_box.update_surfaces()
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