from pygame import Surface
from pygame.event import Event
from pygame.font import Font

from .render.intro_scr import IntroScr
from .render.renderable import Renderable
from .utils.save_operations.check_save import save_exists

from .render.menu.main_menu import Menu


class StateHandler(Renderable):
    def __init__(self, screen: Surface) -> None:
        super().__init__(screen, self.change_state)
        self.screen: Surface = screen
        if not save_exists():
            self.state: Renderable = IntroScr(
                self.screen, self.change_state, Font(None, 32)
            )
        else:
            self.state: Renderable = Menu(self.screen, self.change_state)

    def render(self) -> None:
        self.state.render()

    def event_check(self, event: Event | None) -> None:
        self.state.event_check(event)

    def change_state(self, new_state: Renderable) -> None:
        self.state = new_state
