import concurrent.futures

from pygame import Rect, Surface
import pygame

from ...utils.note_renderer import NoteRenderer
from ...utils.save_operations.read_save import Save
from ..renderable import Renderable
from ..staff import Staff
from .top_menu import TopMenu
from .mod_1.layout import Module1


class Menu(Renderable):
    def __init__(self, screen: Surface, change_state: classmethod) -> None:
        super().__init__(screen, change_state)
        self.screen = screen
        self.staff = Staff(screen)
        self.change_state = change_state
        self.c3_position = self.staff.c3_position
        self.note_renderer = NoteRenderer(screen)
        self.save = Save.load()
        self.total_chapters, self.completed_chapters, self.perfected_chapters = (
            self.__get_modules_data()
        )
        self.cleff_width = self.staff.trebble_cleff_asset.get_width() // 2
        self.modules = [
            Module1(
                screen,
                self.staff,
                change_state,
                self.cleff_width,
                (self.screen.get_width() // 2) - self.cleff_width,
            ),
        ]

    def render(self):
        self.screen.fill("white")
        for module in self.modules:
            module.render()

        self.staff.render(render_time_signature=False)
        TopMenu(
            self.screen,
            completed_chapters=self.completed_chapters,
            perfected_chapters=self.perfected_chapters,
            total_chapters=self.total_chapters,
        ).render()

    def event_check(self, event):
        for module in self.modules:
            module.event_check(event)
        return super().event_check(event)

    def __get_modules_data(self):
        chapter_count = 0
        completed = 0
        perfected = 0

        def count_chapters(module):
            nonlocal chapter_count, completed, perfected
            for chapter in module.chapters:
                chapter_count += 1
                if chapter["completed"]:
                    completed += 1
                if chapter["perfected"]:
                    perfected += 1

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(count_chapters, module)
                for module in self.save.__dict__.values()
            ]
            concurrent.futures.wait(futures)

        return chapter_count, completed, perfected
