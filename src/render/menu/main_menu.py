import concurrent.futures
from typing import List

import pygame.image
from pygame import Surface
from pygame.event import Event

from .mod_1.layout import Module1
from .mod_2.layout import Module2
from .mod_3.layout import Module3
from .top_menu import TopMenu
from ..staff import Staff
from ...utils.image_rescaler import ImageRescaler
from ...utils.module_model import ModuleClass
from ...utils.renderable import Renderable
from ...utils.root_dir import root_dir
from ...utils.save_operations.read_save import Save


class Menu(Renderable):
    def __init__(self, screen: Surface, change_state) -> None:
        super().__init__(screen, change_state)
        self.screen = screen
        self.__staff = Staff(screen)
        self.change_state = change_state
        self.save = Save.load()
        self.__total_chapters, self.__completed_chapters, self.__perfected_chapters = (
            self.__get_modules_data()
        )
        self.__cleff_width = self.__staff.trebble_cleff_asset.get_width()
        mod_width = (self.screen.get_width() // 2 - self.__cleff_width) * 2

        self.__arrow_height = 26
        self.__arrow_y = self.screen.get_height() // 4
        self.__arrow_right = ImageRescaler.rescale_from_height(pygame.image.load(root_dir + "/assets/images/right_triangle.png"),
                                                               self.__arrow_height)
        self.__arrow_left = pygame.transform.flip(self.__arrow_right, True, False)
        self.__arrow_left_x = self.__cleff_width
        self.__arrow_right_x = self.screen.get_width() - self.__arrow_right.get_width() - self.__cleff_width

        self.current_module = self.save.last_opened

        self.modules: List[ModuleClass] = [
            Module1(screen, self.__staff, change_state, self.__cleff_width, mod_width, self.save.md1),
            Module2(screen, self.__staff, change_state, self.__cleff_width, mod_width, self.save.md2),
            Module3(screen, self.__staff, change_state, self.__cleff_width, mod_width, self.save.md2),
        ]

    def render(self):
        self.screen.fill("white")
        self.modules[self.current_module].render()

        if self.current_module > 0:
            self.screen.blit(self.__arrow_left, (self.__arrow_left_x, self.__arrow_y))
        if self.current_module < len(self.modules) - 1:
            self.screen.blit(self.__arrow_right, (self.__arrow_right_x, self.__arrow_y))

        self.__staff.render(render_time_signature=False)
        TopMenu(
            self.screen,
            completed_chapters=self.__completed_chapters,
            perfected_chapters=self.__perfected_chapters,
            total_chapters=self.__total_chapters,
        ).render()

    def event_check(self, event_arg: Event):
        self.modules[self.current_module].event_check(event_arg)
        if event_arg.type == pygame.MOUSEBUTTONDOWN:
            if self.__arrow_left.get_rect(topleft=(self.__arrow_left_x, self.__arrow_y)).collidepoint(
                    event_arg.pos) and self.current_module > 0:
                self.current_module = (self.current_module - 1) % len(self.modules)
                save = Save.load()
                save.last_opened = self.current_module
                save.save()
            elif self.__arrow_right.get_rect(topleft=(self.__arrow_right_x, self.__arrow_y)).collidepoint(
                    event_arg.pos) and self.current_module < len(self.modules) - 1:
                self.current_module = (self.current_module + 1) % len(self.modules)
                save = Save.load()
                save.last_opened = self.current_module
                save.save()
        return super().event_check(event_arg)

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
