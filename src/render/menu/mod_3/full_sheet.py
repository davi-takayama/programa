import re

import numpy as np
import pygame
import sounddevice as sd
from pygame import Surface
from pygame.event import Event

from src.render.staff import Staff
from src.utils.audioinput.audio_analyzer import AudioAnalyzer
from src.utils.audioinput.threading_helper import ProtectedList
from src.utils.button import Button
from src.utils.challenge_model import ChallengeBase
from src.utils.metronome import Metronome
from src.utils.note_renderer import NoteRenderer
from src.utils.save_operations.read_save import Save

vol = 0


class Challenge(ChallengeBase):
    def __init__(
            self,
            screen: Surface,
            change_state,
            chapter_index: int
    ) -> None:
        self.__start_audio_devices()
        super().__init__(screen, change_state, chapter_index)
        self.staff = Staff(screen, self.screen.get_height() // 4, (4, 4))
        self.note_renderer = NoteRenderer(self.screen, self.staff.c3_position)
        self.__bottom_staff = Staff(screen, screen.get_height() // 2, (4, 4))
        self.__bottom_note_renderer = NoteRenderer(self.screen, self.__bottom_staff.c3_position)

        d___c___ = [("D", 0.5), ("C", 0.5)]
        c___c___d___e___ = [("C", 0.25), ("C", 0.25), ("D", 0.25), ("E", 0.25)]
        g___f___e___d___ = [("G", 0.25), ("F", 0.25), ("E", 0.25), ("D", 0.25)]
        e___e___f___g___ = [("E", 0.25), ("E", 0.25), ("F", 0.25), ("G", 0.25)]

        self.__full_sheet: list[tuple[str, float]] = [
            e___e___f___g___, g___f___e___d___, c___c___d___e___, [("E", 0.5), ("D", 0.5)],
            e___e___f___g___, g___f___e___d___, c___c___d___e___, d___c___,

            [("D", 0.25), ("D", 0.25), ("E", 0.25), ("C", 0.25)], [("D", 0.25), ("E", 0.125), ("F", 0.125), ("E", 0.25), ("C", 0.25)],
            [("D", 0.25), ("E", 0.125), ("F", 0.125), ("E", 0.25), ("D", 0.25)], [("C", 0.25), ("D", 0.25), ("G", 0.5)],
            e___e___f___g___, g___f___e___d___, c___c___d___e___, d___c___,
        ]
        self.num_challenges = 4
        self.__curr_bars = self.__full_sheet[:len(self.__full_sheet) // 4]
        self.__back_button = self.init_back_button(self.__close_threads)
        self.__continue_button = self.init_continue_button(self.__click_continue)
        self.__end_button = self.init_end_button(self.__click_end)
        self.__start_button = self.__init_start_button()
        self.__played: list[tuple[str, float]] = []
        self.__audio_processed = False
        self.__metronome = Metronome(60)

        def create_notes_dict(c3_position, note_spacing):
            return {
                'C': c3_position,
                'D': c3_position - note_spacing,
                'E': c3_position - note_spacing * 2,
                'F': c3_position - note_spacing * 3,
                'G': c3_position - note_spacing * 4,
            }

        self.__top_notes_dict = create_notes_dict(self.staff.c3_position, self.staff.note_spacing)
        self.__bottom_notes_dict = create_notes_dict(self.__bottom_staff.c3_position, self.__bottom_staff.note_spacing)

        self.__started_challenge = False
        self.__finished_challenge = False

    def render(self):
        self.screen.fill("white")
        if self.current_challenge < self.num_challenges:
            self.render_challenge_info()
            self.staff.render()
            self.__bottom_staff.render()
            self.__back_button.render()

            self.__render_top_sheet()
            self.__render_bottom_sheet()

            if not self.__started_challenge and not self.__finished_challenge:
                self.__start_button.render()
                text = "Analise a partitura e clique em iniciar para começar o desafio"
                text_width = self.font.size(text)[0]
                self.screen.blit(
                    self.font.render(text, True, "black"),
                    (self.screen.get_width() // 2 - text_width // 2, self.screen.get_height() // 3 * 2)
                )
            else:
                text = "Comece a tocar em: X"
                if self.__start_time + self.__metronome.get_cycle_time() * 5 <= pygame.time.get_ticks():
                    self.__end_current_challenge()
                elif self.__start_time + self.__metronome.get_cycle_time() <= pygame.time.get_ticks():
                    text = "Toque!"
                    self.__get_audio()
                if self.__started_challenge and not self.__finished_challenge:
                    cycle_time = self.__metronome.get_cycle_time()
                    elapsed_time = pygame.time.get_ticks() - self.__start_time
                    ticks_per_cycle = self.__metronome.time_signature[0]
                    time_per_tick = cycle_time // ticks_per_cycle
                    elapsed_ticks = elapsed_time // time_per_tick
                    remaining_ticks = ticks_per_cycle - elapsed_ticks
                    text = text.replace("X", str(remaining_ticks))
                    text_width = self.font.size(text)[0]
                    text_height = self.font.size(text)[1]
                    self.screen.blit(
                        self.font.render(text, True, "black"),
                        (self.screen.get_width() // 2 - text_width // 2, self.screen.get_height() - text_height - 10),
                    )
            if self.__finished_challenge:
                self.__continue_button.render()

        else:
            self.end_render()
            self.__end_button.render()

    def __render_top_sheet(self):
        x_pos = [self.staff.start_x + i * 70 for i in
                 range(len(self.__curr_bars[0]))]
        self.__render_notes(x_pos, self.__curr_bars[0])

        pygame.draw.line(self.screen, "black", (x_pos[-1] + 72, self.staff.line_positions[0]),
                         (x_pos[-1] + 72, self.staff.line_positions[-1]), 5)

        x_pos2 = [x_pos[-1] + 140 + i * 70 for i in range(len(self.__curr_bars[1]))]
        self.__render_notes(x_pos2, self.__curr_bars[1])

    def __render_bottom_sheet(self):
        x_pos = [self.staff.start_x + i * 70 for i in
                 range(len(self.__curr_bars[2]))]
        self.__render_notes(x_pos, self.__curr_bars[2], False)

        pygame.draw.line(self.screen, "black", (x_pos[-1] + 72, self.__bottom_staff.line_positions[0]),
                         (x_pos[-1] + 72, self.__bottom_staff.line_positions[-1]), 5)

        x_pos2 = [x_pos[-1] + 140 + i * 70 for i in range(len(self.__curr_bars[3]))]
        self.__render_notes(x_pos2, self.__curr_bars[3], False)

    def event_check(self, event_arg: Event):
        if event_arg.type == pygame.QUIT:
            self.__close_threads()

            from ..main_menu import Menu
            self.change_state(Menu(self.screen, self.change_state))

        if self.current_challenge < self.num_challenges:
            self.go_back_button.event_check(event_arg)

            if not self.__started_challenge and not self.__finished_challenge:
                self.__start_button.event_check(event_arg)

            elif not self.__started_challenge and self.__finished_challenge:
                self.__continue_button.event_check(event_arg)

        else:
            self.__end_button.event_check(event_arg)

    def __render_notes(self, x_pos, notes, top=True):
        notes_dict = self.__top_notes_dict if top else self.__bottom_notes_dict
        renderer = self.note_renderer if top else self.__bottom_note_renderer

        for i in range(len(notes)):
            if np.isclose(notes[i][1], 0.125, rtol=1e-09, atol=1e-09):
                self.__render_eighth_note(x_pos, notes, i, renderer, notes_dict)
            elif np.isclose(notes[i][1], 0.25, rtol=1e-09, atol=1e-09):
                self.__render_note(x_pos, notes, i, renderer, notes_dict, renderer.quarter, 2)
            elif np.isclose(notes[i][1], 0.5, rtol=1e-09, atol=1e-09):
                self.__render_note(x_pos, notes, i, renderer, notes_dict, renderer.half, 1)

    def __render_eighth_note(self, x_pos, notes, i, renderer, notes_dict):
        if notes[i][0] == 'P':
            renderer.pause(x_pos[i], 3, shift=True)
        else:
            if i + 1 < len(notes) and notes[i + 1][0] != 'P' and np.isclose(
                    notes[i + 1][1], 0.125, rtol=1e-09, atol=1e-09):
                renderer.eighth(
                    [(x_pos[i], notes_dict[notes[i][0]]), (x_pos[i + 1], notes_dict[notes[i + 1][0]])])
            elif i - 1 >= 0 and notes[i - 1][0] != 'P' and np.isclose(
                    notes[i - 1][1], 0.125, rtol=1e-09, atol=1e-09):
                return
            else:
                self.note_renderer.eighth([(x_pos[i], notes_dict[notes[i][0]])])

    @staticmethod
    def __render_note(x_pos, notes, i, renderer, notes_dict, render_method, pause_value):
        if notes[i][0] != "P":
            render_method(x_pos[i], notes_dict[notes[i][0]])
        else:
            renderer.pause(x_pos[i], pause_value, shift=True)

    def __get_audio(self):
        global vol
        freq = self.__queue.get()
        note = "P"
        if freq is not None:
            note = self.analyzer.frequency_to_note_name(freq, 440)
            note = re.sub(r"\d", "", note)

        self.__played.append((note, vol))

    def __start_audio_devices(self):
        def get_volume(indata, *_):
            global vol

            volume_norm = np.linalg.norm(indata) * 10
            vol = round(volume_norm, 2)

        self.__queue = ProtectedList()
        self.analyzer = AudioAnalyzer(self.__queue)
        self.analyzer.start()

        self.stream = sd.InputStream(callback=get_volume)
        self.stream.start()

    def __close_threads(self):
        try:
            self.stream.stop()
            self.stream.close()
            self.analyzer.stop()
            self.analyzer.join()
            self.__metronome.stop()
        except AttributeError:
            pass

    def process_audio(self):
        audio = self.__played.copy()

        def calculate_mean_vol_threshold():
            volume_array = [volume for note, volume in audio if note != "P"]
            if len(volume_array) > 0 and not np.isnan(volume_array).any() and not np.isinf(volume_array).any():
                return np.mean(volume_array) * 0.7
            return 0

        bar_list = []
        num_sections = len(self.__curr_bars)

        for i in range(num_sections):
            start = int(len(audio) * i / num_sections)
            end = int(len(audio) * (i + 1) / num_sections)
            bar_list.append(audio[start:end])

        for index, item in enumerate(bar_list):
            item = self.__find_threshold_meet(item, calculate_mean_vol_threshold())
            item = self.__round_played_values(item)
            bar_list[index] = item

        self.__audio_processed = True
        self.__played = []

        self.calculate_score(bar_list)

    @staticmethod
    def __find_threshold_meet(audio, mean_vol_threshold):
        threshold_meet = []
        length = 0

        for i in range(len(audio)):
            if audio[i][1] > mean_vol_threshold:
                length += 1
            else:
                if length > 0:
                    track = audio[i - length: i]
                    notes = [note[0] for note in track]
                    threshold_meet.append((set(notes), length))
                length = 0

        if length > 0:
            track = audio[-length:]
            notes = [note[0] for note in track]
            most_common_note = max(set(notes), key=notes.count)
            threshold_meet.append((most_common_note, length))

        return threshold_meet

    @staticmethod
    def __round_played_values(note_list) -> list[tuple[set[str], float]]:
        rounded_array = []
        total_sum = sum([item[1] for item in note_list])
        for item in note_list:
            fraction = item[1] / total_sum
            possible_values = [0.125, 0.25, 0.5]
            rounded = min(possible_values, key=lambda x, fraction_arg=fraction: abs(x - fraction_arg))
            rounded_array.append((item[0], rounded))

        return rounded_array

    def calculate_score(self, bar_list):
        for i, bar in enumerate(bar_list):
            obtainable_score = len(bar)
            for j, item in enumerate(bar):
                if j < len(self.__curr_bars[i]):
                    if any(note in self.__curr_bars[i][j][0] for note in item[0]):
                        self.score += 0.5 / obtainable_score / len(bar_list)
                    if np.isclose(item[1], self.__curr_bars[bar_list.index(bar)][bar.index(item)][1], rtol=1e-09, atol=1e-09):
                        self.score += 0.5 / obtainable_score / len(bar_list)

    def __init_start_button(self):
        def callback():
            if self.__metronome.is_alive():
                self.__metronome.restart()
            else:
                self.__metronome.start()
            self.__metronome.playing = True
            self.__start_time = pygame.time.get_ticks()
            self.__started_challenge = True

        text = "Iniciar desafio"
        button = Button(
            self.screen,
            (
                self.screen.get_width() // 2 - (self.font.size("Iniciar desafio")[0] // 2) - 10,
                self.screen.get_height() - 50,
            ),
            text,
            self.font,
            callback,
        )

        return button

    def __click_continue(self):
        self.__metronome.playing = False
        self.current_challenge += 1
        self.__played = []
        if self.current_challenge < self.num_challenges:
            self.__curr_bars = []

            for i in range(self.current_challenge * 4, (self.current_challenge + 1) * 4):
                self.__curr_bars.append(self.__full_sheet[i])
        else:
            self.__close_threads()
        self.__finished_challenge = False
        self.__audio_processed = False
        self.__start_time = 0
        self.__started_challenge = False

    def __click_end(self):
        from ..main_menu import Menu
        self.change_state(Menu(self.screen, self.change_state))
        save = Save.load()
        percent_score = self.score / self.num_challenges
        if percent_score >= 0.7:
            save.md3.chapters[self.chapter_index]["completed"] = True
        if self.score == self.num_challenges:
            save.md3.chapters[self.chapter_index]["perfected"] = True

        if len(save.md3.chapters) > self.chapter_index + 1:
            save.md3.chapters[self.chapter_index + 1]["unlocked"] = True
        Save.save(save)

        from ..main_menu import Menu
        self.change_state(Menu(self.screen, self.change_state))

    def __end_current_challenge(self):
        self.__finished_challenge = True
        self.__started_challenge = False
        if self.__metronome.playing:
            self.__metronome.playing = False
        if not self.__audio_processed:
            self.process_audio()
