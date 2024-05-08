from pygame import Surface
from pygame.font import Font

from ..utils.button import Button


def bottom_screen_button(screen: Surface, on_click) -> Button:
    button_text = "Continuar"
    button_font = Font(None, 48)
    text_width, text_height = button_font.size(button_text)
    screen_width, screen_height = screen.get_size()
    button_padding = 11

    button_x = screen_width - text_width - (button_padding * 2) - 10
    button_y = screen_height - text_height - button_padding - 10
    return Button(
        screen=screen,
        text=button_text,
        pos=(button_x, button_y),
        font=button_font,
        on_click=on_click,
    )
