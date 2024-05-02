from pygame import Rect, Surface
import pygame

from ...staff import Staff
from ...renderable import Renderable
from ....utils.note_renderer import NoteRenderer


class Module1(Renderable):

    def __init__(
        self,
        screen: Surface,
        staff: Staff,
        change_state: classmethod,
        x_pos: int,
        width: int,
    ) -> None:
        super().__init__(screen, change_state)
        self.staff = staff
        self.surface = Surface((width, screen.get_height()))
        self.change_state = change_state
        self.c3 = staff.c3_position
        self.note_renderer = NoteRenderer(self.surface)
        chord_height = self.staff.line_spacing * 3
        self.chord_rect = Rect(
            x_pos + 20,
            self.c3 - chord_height + self.staff.note_spacing,
            20,
            chord_height,
        )

    def render(self):
        self.surface.fill("white")
        self.render_chord()
        self.screen.blit(self.surface, (50, 0))

    def event_check(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.chord_rect.collidepoint(event.pos):
                from .explanation import Explanation1

                self.change_state(Explanation1(self.screen, self.change_state))

    def render_chord(self):
        for i in range(3):
            self.note_renderer.quarter(
                x_pos=20, y_pos=self.c3 - (self.staff.line_spacing * i)
            )
