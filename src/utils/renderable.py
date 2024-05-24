from abc import ABC, abstractmethod

from pygame import Surface
from pygame.event import Event


class Renderable(ABC):

    def __init__(self, screen: Surface, change_state) -> None:
        self.screen = screen
        self.change_state = change_state
        super().__init__()

    @abstractmethod
    def render(self):
        pass

    @abstractmethod
    def event_check(self, event_arg: Event):
        pass
