import functools
from abc import ABC, abstractmethod

import pygame

class Renderable(ABC):
    @abstractmethod
    def render(self):
        pass

    @abstractmethod
    def event_check(self, event_arg: pygame.event.Event | None = None):
        pass
