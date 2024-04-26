from pygame import Surface
from pygame.event import Event
from pygame.font import Font

from .render.intro_scr import IntroScr
from .render.renderable import Renderable
from .utils.check_save import check_save


class StateHandler(Renderable):
    def __init__(self, screen: Surface) -> None:
        super().__init__()
        self.screen: Surface = screen
        if not check_save():
            self.state: Renderable = IntroScr(self.screen, Font(None, 32))
        else:
            self.state: Renderable = self.PlaceholderState(self.screen)

    def render(self) -> None:
        self.state.render()

    def event_check(self, event: Event | None) -> None:
        self.state.event_check(event)

    class PlaceholderState(Renderable):
        def __init__(self, screen: Surface) -> None:
            super().__init__()
            self.screen = screen

        def render(self) -> None:
            self.screen.fill("black")

        def event_check(self, event) -> None:
            """
            Placeholder event check
            """
            pass
