import textwrap

from pygame import Surface, Rect
from pygame.event import Event
from pygame.font import Font

from src.utils.bottom_screen_button import bottom_screen_button
from src.utils.note_renderer import NoteRenderer
from src.utils.renderable import Renderable
from src.utils.save_operations.read_save import Save


class Explanation(Renderable):
    def __init__(self, screen: Surface, change_state) -> None:
        super().__init__(screen, change_state)

        self.__top_text = "Em uma partitura, podemos encontrar outros elementos que indicam duração além de notas."
        self.bottom_text = "Cada nota tem uma pausa de duração equivalente e, nestas, nada é tocado."

        def click_continue():
            save = Save.load()
            save.md2.chapters[1]["unlocked"] = True
            save.save()

            from ..main_menu import Menu
            self.change_state(Menu(self.screen, self.change_state))

        self.__continue_button = bottom_screen_button(self.screen, click_continue)
        self.__font = Font(None, 48)
        self.note_renderer = NoteRenderer(screen, draw_lines=False)

    def render(self):
        self.screen.fill("white")
        top_text_rect = Rect(0, 0, self.screen.get_width(), self.screen.get_height() // 3)
        bottom_text_rect = Rect(self.screen.get_width() // 2,
                                self.screen.get_height() // 3,
                                self.screen.get_width() // 2,
                                (self.screen.get_height() // 3) * 2)
        notes_and_pauses_rect = Rect(0,
                                     self.screen.get_height() // 3,
                                     self.screen.get_width() // 2,
                                     (self.screen.get_height() // 3) * 2)

        def draw_text(text: str, rect_arg: Rect, width: int):
            wrapped_text = textwrap.wrap(text, width=width)
            total_text_height = len(wrapped_text) * self.__font.get_height()

            for index_, text in enumerate(wrapped_text):
                text_surface = self.__font.render(text, True, "black")
                text_rect = text_surface.get_rect(center=rect_arg.center)
                text_rect.y = rect_arg.centery - total_text_height // 2 + index_ * text_rect.height
                self.screen.blit(text_surface, text_rect)

        draw_text(self.__top_text, top_text_rect, 50)
        draw_text(self.bottom_text, bottom_text_rect, 20)

        rects = [Rect(notes_and_pauses_rect.x + (i % 2) * notes_and_pauses_rect.width // 2,
                      notes_and_pauses_rect.y + (i // 2) * notes_and_pauses_rect.height // 2,
                      notes_and_pauses_rect.width // 2,
                      notes_and_pauses_rect.height // 2) for i in range(4)]

        def draw_on_rect(rect_arg, note: int):
            match note:
                case 0:
                    self.note_renderer.whole(rect_arg.centerx - 32, rect_arg.centery)
                    self.note_renderer.pause(rect_arg.centerx + 32, note, rect_arg.centery)
                case 1:
                    self.note_renderer.half(rect_arg.centerx - 32, rect_arg.centery)
                    self.note_renderer.pause(rect_arg.centerx + 32, note, rect_arg.centery)
                case 2:
                    self.note_renderer.quarter(rect_arg.centerx - 32, rect_arg.centery)
                    self.note_renderer.pause(rect_arg.centerx + 32, note, rect_arg.centery)
                case 3:
                    self.note_renderer.single_eighth(rect_arg.centerx - 32, rect_arg.centery)
                    self.note_renderer.pause(rect_arg.centerx + 32, note, rect_arg.centery)
                case _:
                    pass

        for index, rect in enumerate(rects):
            draw_on_rect(rect, index)

        self.__continue_button.render()

    def event_check(self, event_arg: Event | None = None):
        self.__continue_button.event_check(event_arg)
