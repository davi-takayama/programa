import random

import numpy as np
import pygame
import sounddevice as sd
from pygame import Surface
from pygame.event import Event

from src.utils.button import Button
from src.utils.challenge_model import ChallengeBase
from src.utils.metronome import Metronome
from src.utils.save_operations.read_save import Save

vol = 0


class Challenge3(ChallengeBase):
    def __init__(self, screen: Surface, change_state, chapter_index: int, use_pauses: bool = False):
        super().__init__(screen, change_state, chapter_index, True)
        self.start_audio_devices()
        self.continue_button = self.init_continue_button(self.click_continue)
        self.back_button = self.init_back_button(self.close_audio_devices)
        self.end_button = self.init_end_button(self.click_end)
        self.start_button = self.init_start_button()
        self.sensibility_button = self.init_sensibility_button()
        self.metronome = Metronome(90, (4, 4))
        self.vol_stream = []
        self.vol_sensibility = 2
        self.start_time = 0
        self.times: list[list[tuple[str, float]]] = [
            [('note', 0.25), ('note', 0.25), ('note', 0.25), ('note', 0.25)],
            [('note', 0.25), ('note', 0.25), ('note', 0.5)],
            [('note', 0.5), ('note', 0.25), ('note', 0.25)],
            [('note', 0.25), ('note', 0.125), ('note', 0.125), ('note', 0.25), ('note', 0.25)],
            [('note', 0.25), ('note', 0.125), ('note', 0.125), ('note', 0.25), ('note', 0.125), ('note', 0.125)],
        ]
        self.times_with_pauses: list[list[tuple[str, float]]] = [
            [("", 0.25), ("", 0.25), ("", 0.25), ("", 0.25)],
            [("", 0.25), ("", 0.25), ("", 0.5)],
            [("", 0.25), ("", 0.125), ("", 0.125), ("", 0.25), ("", 0.25)],
            [("", 0.25), ("", 0.125), ("", 0.125), ("", 0.25), ("", 0.125), ("", 0.125)],
            [("", 0.125), ("", 0.125), ("", 0.125), ("", 0.125), ("", 0.25), ("", 0.125), ("", 0.125)],
        ]
        self.curr_rythm = self.times[self.current_challenge] if not use_pauses else self.random_challenge()
        self.played: list[tuple[str, tuple[int, int]]] = []
        self.num_challenges = len(self.times)
        self.started_challenge = False
        self.finished_challenge = False
        self.y_pos: int = int(self.staff.line_positions[3] - self.staff.note_spacing)
        self.stream_processed = False
        self.use_pauses = use_pauses

    def render(self):
        self.screen.fill("white")

        if self.current_challenge == self.num_challenges:
            self.end_render()
            self.end_button.render()
        else:
            self.render_challenge()
            self.render_challenge_info()

    def render_challenge(self):
        self.back_button.render()
        self.staff.render()
        possible_area = (self.screen.get_width() // 2) - self.staff.start_x
        x_pos = [int(self.staff.start_x + i * (possible_area / len(self.curr_rythm))) for i in range(len(self.curr_rythm))]
        self.render_notes(x_pos, self.curr_rythm)
        line_y_start = self.staff.line_positions[0]
        line_y_end = self.staff.line_positions[-1]
        pygame.draw.line(
            self.screen,
            "black",
            (self.screen.get_width() // 2, line_y_start),
            (self.screen.get_width() // 2, line_y_end),
            4
        )

        if not self.started_challenge and not self.finished_challenge:
            self.start_button.render()
            self.sensibility_button.render()
            text = "Analise a partitura e clique em iniciar para começar o desafio"
            text_width = self.font.size(text)[0]
            self.screen.blit(
                self.font.render(text, True, "black"),
                (self.screen.get_width() // 2 - text_width // 2, self.screen.get_height() // 2)
            )

        else:
            text = "Comece a tocar em: X"
            if self.start_time + self.metronome.get_cycle_time() * 2 <= pygame.time.get_ticks():
                self.end_current_challenge()
            elif self.start_time + self.metronome.get_cycle_time() <= pygame.time.get_ticks():
                text = "Toque!"
                self.get_volume_stream()
            if self.started_challenge and not self.finished_challenge:
                cycle_time = self.metronome.get_cycle_time()
                elapsed_time = pygame.time.get_ticks() - self.start_time
                ticks_per_cycle = self.metronome.time_signature[0]
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
        if self.finished_challenge:
            self.continue_button.render()
            if self.stream_processed:
                half_screen_width = self.screen.get_width() // 2
                num_played = len(self.played)
                x_pos = [half_screen_width + 20 + i * (possible_area // num_played) for i in range(num_played)]
                self.render_notes(x_pos, self.played)
                text = "Você tocou:"
                text_width = self.font.size(text)[0]
                text_y_pos = self.staff.line_positions[0] - self.staff.note_spacing * 4
                self.screen.blit(
                    self.font.render(text, True, "black"),
                    (half_screen_width * 1.5 - text_width // 2, text_y_pos)
                )

    def end_current_challenge(self):
        self.finished_challenge = True
        self.started_challenge = False
        if self.metronome.playing:
            self.metronome.playing = False
        if not self.stream_processed:
            self.process_audio_stream()

    def render_notes(self, x_pos, notes):
        for i in range(len(notes)):
            if np.isclose(notes[i][1], 0.125, rtol=1e-09, atol=1e-09):
                self.render_eighth_note(x_pos, notes, i)
            elif np.isclose(notes[i][1], 0.25, rtol=1e-09, atol=1e-09):
                self.render_quarter_note(x_pos, notes, i)
            elif np.isclose(notes[i][1], 0.5, rtol=1e-09, atol=1e-09):
                self.render_half_note(x_pos, notes, i)

    def render_eighth_note(self, x_pos, notes, i):
        if notes[i][0] == 'pause':
            self.note_renderer.pause(x_pos[i], 3, shift=True)
        else:
            if i + 1 < len(notes) and notes[i + 1][0] == 'note' and np.isclose(
                    notes[i + 1][1], 0.125, rtol=1e-09, atol=1e-09):
                self.note_renderer.eighth([(x_pos[i], self.y_pos), (x_pos[i + 1], self.y_pos)])
            elif i - 1 >= 0 and notes[i - 1][0] == 'note' and np.isclose(
                    notes[i - 1][1], 0.125, rtol=1e-09, atol=1e-09):
                return
            else:
                self.note_renderer.eighth([(x_pos[i], self.y_pos)])

    def render_quarter_note(self, x_pos, notes, i):
        if notes[i][0] == "note":
            self.note_renderer.quarter(x_pos[i], self.y_pos)
        else:
            self.note_renderer.pause(x_pos[i], 2, shift=True)

    def render_half_note(self, x_pos, notes, i):
        if notes[i][0] == "note":
            self.note_renderer.half(x_pos[i], self.y_pos)
        else:
            self.note_renderer.pause(x_pos[i], 1, shift=True)

    def event_check(self, event_arg: Event):
        if event_arg.type == pygame.QUIT:
            try:
                self.close_audio_devices()
            except AttributeError:
                pass
        if self.current_challenge < self.num_challenges:
            self.check_challenge(event_arg)
        else:
            self.end_button.event_check(event_arg)

    def check_challenge(self, event_arg):
        if self.current_challenge == self.num_challenges:
            self.end_button.event_check(event_arg)
        if self.current_challenge < self.num_challenges:
            self.back_button.event_check(event_arg)
            if not self.started_challenge and not self.finished_challenge:
                self.start_button.event_check(event_arg)
                self.sensibility_button.event_check(event_arg)

            elif not self.started_challenge and self.finished_challenge:
                self.continue_button.event_check(event_arg)

    def click_end(self):
        save = Save.load()
        chapter = save.md2.chapters[self.chapter_index]

        chapter["completed"] = self.score >= self.num_challenges * 0.7
        chapter["perfected"] = self.score == self.num_challenges

        if self.chapter_index + 1 < len(save.md2.chapters):
            next_chapter = save.md2.chapters[self.chapter_index + 1]
            next_chapter["unlocked"] = self.score >= self.num_challenges * 0.7
        else:
            save.md3.unlocked = True
        save.md2.chapters[self.chapter_index] = chapter
        save.save()

        try:
            self.close_audio_devices()
        except AttributeError:
            pass

        try:
            self.metronome.playing = False
            self.metronome.running = False
            self.metronome.stop()
            self.metronome.join()
        except RuntimeError:
            pass

        from ..main_menu import Menu

        self.change_state(Menu(self.screen, self.change_state))

    def click_continue(self):
        self.metronome.playing = False
        self.current_challenge += 1
        self.vol_stream = []
        self.played = []
        if self.current_challenge < self.num_challenges:
            self.curr_rythm = self.times[self.current_challenge] if not self.use_pauses else self.random_challenge()
            self.finished_challenge = False
            self.stream_processed = False
            self.start_time = 0
            self.started_challenge = False

    def get_volume_stream(self):
        global vol
        self.vol_stream.append(vol)

    def start_audio_devices(self):
        def get_volume(indata, *_):
            global vol
            vol = round(np.linalg.norm(indata) * 10, 2)

        self.stream = sd.InputStream(callback=get_volume)
        self.stream.start()
        self.vol_sensibility = self.init_sensibility_button().on_click()

    def close_audio_devices(self):
        try:
            self.stream.stop()
            self.stream.close()
        except AttributeError:
            pass

        try:
            self.metronome.playing = False
            self.metronome.running = False
            self.metronome.stop()
            self.metronome.join()
        except RuntimeError:
            pass

    def init_sensibility_button(self):
        def callback():
            global vol
            self.vol_sensibility = (vol * 1.2) if vol > 1.5 else 2

        text = "Ajustar sensibilidade"
        x = self.screen.get_width() - self.font.size(text)[0] - 30
        y = self.screen.get_height() - self.font.size(text)[1] - 20
        button = Button(
            self.screen,
            (x, y),
            text,
            self.font,
            callback,
        )

        return button

    def init_start_button(self):
        def callback():
            if self.metronome.is_alive():
                self.metronome.restart()
            else:
                self.metronome.start()
            self.metronome.playing = True
            self.start_time = pygame.time.get_ticks()
            self.started_challenge = True

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

    def random_challenge(self):
        num_challenges_available = len(self.times_with_pauses)
        rng = np.random.default_rng(seed=69)
        index = rng.integers(0, num_challenges_available)
        challenge = self.times_with_pauses[index].copy()
        random.shuffle(self.times_with_pauses[index])
        for i in range(len(challenge)):
            challenge[i] = ('note', challenge[i][1])
        num_pauses = random.randint(1, len(challenge) // 3 if len(challenge) > 3 else 1)
        pause_indices: set[int] = set()

        for i in range(num_pauses):
            pause_index = random.randint(1, len(challenge) - 2)
            while pause_index - 1 in pause_indices or pause_index + 1 in pause_indices or pause_index in pause_indices:
                pause_index = random.randint(1, len(challenge) - 2)
            pause_indices.add(pause_index)

        for i in pause_indices:
            challenge[i] = ('pause', challenge[i][1])
        self.times_with_pauses.pop(index)
        return challenge

    def process_audio_stream(self):
        self.played = []  # [(type, (start, length)), ...]
        mean_vol_threshold = self.calculate_mean_vol_threshold()

        audio_stream = self.filter_audio_stream(self.vol_stream, self.vol_sensibility)

        threshold_meet = self.find_threshold_meet(audio_stream, mean_vol_threshold)
        self.played = self.convert_threshold_meet_to_played(threshold_meet)

        self.insert_pauses_between_notes()
        self.join_adjacent_pauses()
        self.round_played_values()

        self.stream_processed = True
        self.calculate_score()

    def calculate_mean_vol_threshold(self):
        if len(self.vol_stream) > 0 and not np.isnan(self.vol_stream).any() and not np.isinf(self.vol_stream).any():
            return np.mean(self.vol_stream) * 0.7
        return 0

    @staticmethod
    def filter_audio_stream(audio_stream, vol_sensibility):
        filtered_stream = audio_stream.copy()
        for i in range(len(filtered_stream)):
            if filtered_stream[i] < vol_sensibility:
                filtered_stream[i] = 0
        return filtered_stream

    @staticmethod
    def find_threshold_meet(audio_stream, mean_vol_threshold):
        threshold_meet = []
        length = 0
        for i in range(len(audio_stream)):
            if audio_stream[i] > mean_vol_threshold:
                length += 1
            else:
                if length > 0:
                    threshold_meet.append((i - length, length))
                length = 0
        if length > 0:
            threshold_meet.append((len(audio_stream) - length, length))
        return threshold_meet

    @staticmethod
    def convert_threshold_meet_to_played(threshold_meet) -> list[tuple[str, tuple[int, int]]]:
        return [("note", (start, start + length)) for start, length in threshold_meet]

    def insert_pauses_between_notes(self):
        aux_arr = []
        for i, item in enumerate(self.played[:-1]):
            next_play = self.played[i + 1]
            aux_arr.append(item)
            if next_play[1][0] - item[1][1] > 0 and item[0] == "note" and next_play[0] == "note":
                aux_arr.append(("pause", (item[1][1], next_play[1][0])))
        aux_arr.append(self.played[-1])
        self.played = aux_arr

    def join_adjacent_pauses(self):
        i = 0
        while i < len(self.played) - 1:
            if self.played[i][0] == "pause" and self.played[i + 1][0] == "pause":
                self.played[i] = ("pause", (self.played[i][1][0], self.played[i + 1][1][1]))
                self.played.pop(i + 1)
            elif self.played[i][0] == "pause" and self.played[i][1][1] - self.played[i][1][0] <= 7:
                self.played[i + 1] = (
                    self.played[i + 1][0],
                    (
                        self.played[i][1][0],
                        self.played[i + 1][1][1]
                    )
                )
                self.played.pop(i)
            else:
                i += 1

    def round_played_values(self):
        rounded_array = []
        for item in self.played:
            fraction = (item[1][1] - item[1][0]) / len(self.vol_stream)
            possible_values = [0.125, 0.25, 0.5]
            rounded = min(possible_values, key=lambda x, fraction_arg=fraction: abs(x - fraction_arg))
            rounded_array.append((item[0], rounded))
        self.played = rounded_array

    def calculate_score(self):
        correct_plays = 0
        for i in range(len(self.played)):
            if i < len(self.curr_rythm) and self.played[i][0] == self.curr_rythm[i][0] and np.isclose(self.played[i][1],
                                                                                                      self.curr_rythm[i][1],
                                                                                                      rtol=1e-09, atol=1e-09):
                correct_plays += 1
        print(f"Correct plays: {correct_plays}; Score: {round(correct_plays / len(self.curr_rythm), 2)}")
        print()
        score = round(correct_plays / len(self.curr_rythm), 2)
        self.score += score
        if score >= 0.7:
            self.correct_se.play()
        else:
            self.incorrect_se.play()
