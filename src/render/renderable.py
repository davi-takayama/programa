from abc import ABC, abstractmethod

from pygame import Surface
from pygame.event import Event


class Renderable(ABC):
    def __init__(self, screen: Surface) -> None:
        self.screen = screen
        super().__init__()

    @abstractmethod
    def render(self):
        pass

    @abstractmethod
    def event_check(self, event_arg: Event | None = None):
        pass
