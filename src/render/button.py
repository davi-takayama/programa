import pygame
from .renderable import Renderable


class Button():
    def __init__(
        self,
        screen: pygame.Surface,
        x: int,
        y: int,
        text: str,
        font: pygame.font.Font,
        on_click,
    ):
        self.screen = screen
        self.x = x
        self.y = y
        self.text = text
        self.font = font
        self.on_click = on_click
        self.width, self.height = self.font.size(self.text)
        self.padding = 10

    def render(self):
        pygame.draw.rect(
            self.screen,
            "white",
            (self.x, self.y, self.width + 2 * self.padding, self.height + self.padding),
            0,
            10,
        )
        pygame.draw.rect(
            self.screen,
            "black",
            (self.x, self.y, self.width + 2 * self.padding, self.height + self.padding),
            1,
            10,
        )
        self.screen.blit(
            self.font.render(self.text, True, "black"),
            (self.x + self.padding, self.y + self.padding // 2),
        )

    def event_check(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            col = pos[0]
            row = pos[1]
            if (
                col >= self.x
                and col <= self.x + self.width + 2 * self.padding
                and row >= self.y
                and row <= self.y + self.height + self.padding
            ):
                self.on_click()