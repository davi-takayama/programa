import pygame


class Button:
    def __init__(
            self,
            screen: pygame.Surface,
            pos: tuple[int, int],
            text: str,
            font: pygame.font.Font,
            on_click,
    ):
        self.screen = screen
        self.pos = pos
        self.text = text
        self.font = font
        self.on_click = on_click
        self.width, self.height = self.font.size(self.text)
        self.padding = 10

    def render(self):
        pygame.draw.rect(
            self.screen,
            "white",
            (
                self.pos[0],
                self.pos[1],
                self.width + 2 * self.padding,
                self.height + self.padding,
            ),
            0,
            10,
        )
        pygame.draw.rect(
            self.screen,
            "black",
            (
                self.pos[0],
                self.pos[1],
                self.width + 2 * self.padding,
                self.height + self.padding,
            ),
            1,
            10,
        )
        self.screen.blit(
            self.font.render(self.text, True, "black"),
            (self.pos[0] + self.padding, self.pos[1] + self.padding // 2),
        )

    def event_check(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            col = pos[0]
            row = pos[1]
            if (
                    self.pos[0] <= col <= self.pos[0] + self.width + 2 * self.padding
                    and self.pos[1] <= row <= self.pos[1] + self.height + self.padding
            ):
                self.on_click()
