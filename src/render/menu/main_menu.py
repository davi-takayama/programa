import concurrent.futures

from pygame import Surface

from ...utils.note_renderer import NoteRenderer
from ...utils.save_operations.read_save import Save
from ..renderable import Renderable
from ..staff import Staff
from .top_menu import TopMenu


class Menu(Renderable):
    def __init__(self, screen: Surface, change_state: classmethod) -> None:
        super().__init__(screen)
        self.screen = screen
        self.staff = Staff(screen)
        self.change_state = change_state
        self.c3_position = self.staff.c3_position
        self.note_renderer = NoteRenderer(screen)
        self.save = Save.load()
        self.total_chapters, self.completed_chapters, self.perfected_chapters = (
            self.__get_chapter_data()
        )

    def render(self):
        self.screen.fill("white")
        self.staff.render(render_time_signature=False)
        TopMenu(
            self.screen,
            completed_chapters=self.completed_chapters,
            perfected_chapters=self.perfected_chapters,
            total_chapters=self.total_chapters,
        ).render()

    def event_check(self, event):
        return super().event_check(event)

    def __make_chord(self, note: str, num_notes: int, x_pos: int, duration: int = 0):
        """
        note: The note to start the chord on
        num_notes: The number of notes in the chord
        x_pos: The x position of the chord
        duration: The duration of the chord (0 = whole, 1 = half, 2 = quarter, 3 = eigth...)
        """
        notes = ["C", "D", "E", "F", "G", "A", "B"]
        note_index = notes.index(note)
        for index, item in enumerate(
            [
                (self.staff.c3_position - self.staff.line_spacing * note_index)
                - self.staff.line_spacing * i
                for i in range(num_notes)
            ]
        ):
            if duration == 0:
                self.note_renderer.whole(self.screen, x_pos, item)
            elif duration == 1:
                self.note_renderer.half(self.screen, x_pos, item)
            elif duration == 2:
                self.note_renderer.quarter(self.screen, x_pos, item)
            elif duration == 3:
                if index == num_notes - 1:
                    self.note_renderer.single_eighth(self.screen, x_pos, item)
                else:
                    self.note_renderer.quarter(self.screen, x_pos, item)

    def __get_chapter_data(self):
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
