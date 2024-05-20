import textwrap
from abc import abstractmethod
from typing import Callable

from pygame import Surface
from pygame.event import Event
from pygame.font import Font

from src.render.staff import Staff
from src.utils.button import Button
from src.utils.note_renderer import NoteRenderer
from src.utils.renderable import Renderable


class ChallengeBase(Renderable):
    def __init__(
            self,
            screen: Surface,
            change_state,
            chapter_index: int,
            use_audio: bool = False,
            num_challenges: int = 10,
    ) -> None:
        super().__init__(screen, change_state)
        self.chapter_index = chapter_index
        self.use_audio = use_audio
        self.num_challenges = num_challenges
        self.current_challenge = 0
        self.staff = Staff(screen, self.screen.get_height() // 3, (4, 4))
        self.score = 0
        self.font = Font(None, size=32)
        self.note_renderer = NoteRenderer(screen, self.staff.c3_position)
        self.go_back_button = self.init_back_button()

    @abstractmethod
    def render(self):
        pass

    @abstractmethod
    def event_check(self, event_arg: Event | None = None):
        pass

    def init_back_button(self, extra_arguments = None):
        def click_back():
            if extra_arguments:
                extra_arguments()
            from ..render.menu.main_menu import Menu

            self.change_state(Menu(self.screen, self.change_state))

        button_text = "Voltar ao menu"

        return Button(self.screen, (20, 20), button_text, self.font, click_back)

    def init_continue_button(self, click_continue: Callable):
        return Button(
            font=self.font,
            text="Continuar",
            on_click=click_continue,
            pos=(
                self.screen.get_width() // 2
                - (self.font.size("Continuar")[0] // 2)
                - 10,
                self.screen.get_height() - 50,
            ),
            screen=self.screen,
        )

    def init_end_button(self, click_end: callable):
        button_text = "Voltar ao menu"
        button_x = self.screen.get_width() // 2 - self.font.size(button_text)[0] // 2
        button_y = (self.screen.get_height() // 4) * 3

        return Button(
            self.screen,
            (button_x, button_y),
            button_text,
            self.font,
            click_end
        )

    def final_screen(self):
        self.screen.fill("white")
        if self.score >= int(self.num_challenges * 0.7):
            text = "Parabéns! Você completou o capítulo!"
        else:
            text = "Você não conseguiu a pontuação para completar o capítulo. Tente novamente!"
        width, _ = self.font.size(text)

        for index, text in enumerate(textwrap.wrap(text, width=60)):
            text_surface = self.font.render(text, True, "black")
            text_rect = text_surface.get_rect()
            text_rect.centerx = self.screen.get_width() // 2
            text_rect.topleft = (
                text_rect.centerx - text_rect.width // 2,
                (self.screen.get_height() // 4)
                + (index * (self.font.size(text)[1] + 10)),
            )
            self.screen.blit(text_surface, text_rect.topleft)

        text = (
                "Sua pontuação foi: " + str(self.score) + "/" + str(self.num_challenges)
        )
        width, _ = self.font.size(text)
        self.screen.blit(
            self.font.render(text, True, "black"),
            (
                (self.screen.get_width() // 2) - (width // 2),
                (self.screen.get_height() // 2),
            ),
        )

    def end_render(self):
        if self.score >= int(self.num_challenges * 0.7):
            text = "Parabéns! Você completou o capítulo!"
        else:
            text = "Você não conseguiu a pontuação para completar o capítulo. Tente novamente!"
        width, _ = self.font.size(text)

        for index, text in enumerate(textwrap.wrap(text, width=60)):
            text_surface = self.font.render(text, True, "black")
            text_rect = text_surface.get_rect()
            text_rect.centerx = self.screen.get_width() // 2
            text_rect.topleft = (
                text_rect.centerx - text_rect.width // 2,
                (self.screen.get_height() // 4)
                + (index * (self.font.size(text)[1] + 10)),
            )
            self.screen.blit(text_surface, text_rect.topleft)

        text = (
                "Sua pontuação foi: " + str(self.score) + "/" + str(self.num_challenges)
        )
        width, _ = self.font.size(text)
        self.screen.blit(
            self.font.render(text, True, "black"),
            (
                (self.screen.get_width() // 2) - (width // 2),
                (self.screen.get_height() // 2),
            ),
        )
