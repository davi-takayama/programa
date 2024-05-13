from abc import abstractmethod

from pygame import Surface
from pygame.event import Event
from pygame.font import Font

from src.render.staff import Staff
from src.utils.button import Button
from src.utils.note_renderer import NoteRenderer
from src.utils.renderable import Renderable
from src.utils.save_operations.read_save import Save


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
        self.end_button = self.init_end_button()
        self.go_back_button = self.init_back_button()

    @abstractmethod
    def render(self):
        pass

    @abstractmethod
    def event_check(self, event_arg: Event | None = None):
        pass

    def init_back_button(self):
        def click_back():
            from ..render.menu.main_menu import Menu

            self.change_state(Menu(self.screen, self.change_state))

        button_text = "Voltar ao menu"

        return Button(self.screen, (20, 20), button_text, self.font, click_back)

    def init_continue_button(self, click_continue: callable):
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

    def init_end_button(self):
        def click_end():
            save = Save.load()
            chapter = save.md1.chapters[self.chapter_index]

            if self.score >= int(self.num_challenges * 0.7):
                chapter["completed"] = True
                if self.score == self.num_challenges:
                    chapter["perfected"] = True
                if self.chapter_index + 1 < len(save.md1.chapters):
                    next_chapter = save.md1.chapters[self.chapter_index + 1]
                    next_chapter["unlocked"] = True
                else:
                    save.md2.unlocked = True
            save.md1.chapters[self.chapter_index] = chapter
            save.save()
            from ..render.menu.main_menu import Menu

            self.change_state(Menu(self.screen, self.change_state))

        button_text = "Voltar ao menu"
        button_x = self.screen.get_width() // 2 - self.font.size(button_text)[0] // 2
        button_y = (self.screen.get_height() // 4) * 3

        return Button(
            self.screen, (button_x, button_y), button_text, self.font, click_end
        )
