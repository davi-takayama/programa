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


class Challenge(ChallengeBase):
    def __init__(self, screen: Surface, change_state, chapter_index: int, use_pauses: bool = False):
        super().__init__(screen, change_state, chapter_index, True)
        self.__start_audio_devices()
        self.__continue_button = self.init_continue_button(self.__click_continue)
        self.__back_button = self.init_back_button(self.__close_audio_devices)
        self.__end_button = self.init_end_button(self.__click_end)
        self.__start_button = self.__init_start_button()
        self.__sensibility_button = self.__init_sensibility_button()
        self.__metronome = Metronome(90, (4, 4))
        self.__vol_stream = []
        self.__vol_sensibility = 2
        self.__start_time = 0
        self.__times: list[list[tuple[str, float]]] = [
            [('note', 0.25), ('note', 0.25), ('note', 0.25), ('note', 0.25)],
            [('note', 0.25), ('note', 0.25), ('note', 0.5)],
            [('note', 0.5), ('note', 0.25), ('note', 0.25)],
            [('note', 0.25), ('note', 0.125), ('note', 0.125), ('note', 0.25), ('note', 0.25)],
            [('note', 0.25), ('note', 0.125), ('note', 0.125), ('note', 0.25), ('note', 0.125), ('note', 0.125)],
        ]
        self.__times_with_pauses: list[list[tuple[str, float]]] = [
            [("", 0.25), ("", 0.25), ("", 0.25), ("", 0.25)],
            [("", 0.25), ("", 0.25), ("", 0.5)],
            [("", 0.25), ("", 0.125), ("", 0.125), ("", 0.25), ("", 0.25)],
            [("", 0.25), ("", 0.125), ("", 0.125), ("", 0.25), ("", 0.125), ("", 0.125)],
            [("", 0.125), ("", 0.125), ("", 0.125), ("", 0.125), ("", 0.25), ("", 0.125), ("", 0.125)],
        ]
        self.__curr_rythm = self.__times[self.current_challenge] if not use_pauses else self.__random_challenge()
        self.__played: list[tuple[str, tuple[int, int]]] = []
        self.num_challenges = len(self.__times)
        self.__started_challenge = False
        self.__finished_challenge = False
        self.__y_pos: int = int(self.staff.line_positions[3] - self.staff.note_spacing)
        self.__stream_processed = False
        self.__use_pauses = use_pauses

    def render(self):
        self.screen.fill("white")

        if self.current_challenge == self.num_challenges:
            self.end_render()
            self.__end_button.render()
        else:
            self.__render_challenge()
            self.render_challenge_info()

    def __render_challenge(self):
        self.__back_button.render()
        self.staff.render()
        x_pos = [int(self.staff.start_x + i * 75) for i in range(len(self.__curr_rythm))]
        self.__render_notes(x_pos)
        if not self.__started_challenge and not self.__finished_challenge:
            self.__start_button.render()
            self.__sensibility_button.render()
            text = "Analise a partitura e clique em iniciar para começar o desafio"
            text_width = self.font.size(text)[0]
            self.screen.blit(
                self.font.render(text, True, "black"),
                (self.screen.get_width() // 2 - text_width // 2, self.screen.get_height() // 2)
            )

        else:
            text = "Comece a tocar em: X"
            if self.__start_time + self.__metronome.get_cycle_time() * 2 <= pygame.time.get_ticks():
                self.__end_current_challenge()
            elif self.__start_time + self.__metronome.get_cycle_time() <= pygame.time.get_ticks():
                text = "Toque!"
                self.__get_volume_stream()
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

    def __end_current_challenge(self):
        self.__finished_challenge = True
        self.__started_challenge = False
        if self.__metronome.playing:
            self.__metronome.playing = False
        if not self.__stream_processed:
            self.process_audio_stream()

    def __render_notes(self, x_pos):
        for i in range(len(self.__curr_rythm)):
            if np.isclose(self.__curr_rythm[i][1], 0.125, rtol=1e-09, atol=1e-09):
                if self.__curr_rythm[i][0] == 'pause':
                    self.note_renderer.pause(x_pos[i], 3)
                else:
                    if i + 1 < len(self.__curr_rythm) and self.__curr_rythm[i + 1][0] == 'note' and np.isclose(
                            self.__curr_rythm[i + 1][1], 0.125, rtol=1e-09, atol=1e-09):
                        self.note_renderer.eighth([(x_pos[i], self.__y_pos), (x_pos[i + 1], self.__y_pos)])
                    elif i - 1 >= 0 and self.__curr_rythm[i - 1][0] == 'note' and np.isclose(
                            self.__curr_rythm[i - 1][1], 0.125, rtol=1e-09, atol=1e-09):
                        continue
                    else:
                        self.note_renderer.eighth([(x_pos[i], self.__y_pos)])

            elif np.isclose(self.__curr_rythm[i][1], 0.25, rtol=1e-09, atol=1e-09):
                if self.__curr_rythm[i][0] == "note":
                    self.note_renderer.quarter(x_pos[i], self.__y_pos)
                else:
                    self.note_renderer.pause(x_pos[i], 2)
            elif np.isclose(self.__curr_rythm[i][1], 0.5, rtol=1e-09, atol=1e-09):
                if self.__curr_rythm[i][0] == "note":
                    self.note_renderer.half(x_pos[i], self.__y_pos)
                else:
                    self.note_renderer.pause(x_pos[i], 1)

    def event_check(self, event_arg: Event):
        if event_arg.type == pygame.QUIT:
            try:
                self.__close_audio_devices()
            except AttributeError:
                pass
        if self.current_challenge < self.num_challenges:
            self.__check_challenge(event_arg)
        else:
            self.__end_button.event_check(event_arg)

    def __check_challenge(self, event_arg):
        if self.current_challenge == self.num_challenges:
            self.__end_button.event_check(event_arg)
        if self.current_challenge < self.num_challenges:
            self.__back_button.event_check(event_arg)
            if not self.__started_challenge and not self.__finished_challenge:
                self.__start_button.event_check(event_arg)
                self.__sensibility_button.event_check(event_arg)

            elif not self.__started_challenge and self.__finished_challenge:
                self.__continue_button.event_check(event_arg)

    def __click_end(self):
        save = Save.load()
        chapter = save.md2.chapters[self.chapter_index]

        if self.score >= self.num_challenges * 0.7:
            chapter["completed"] = True
            if self.score == self.num_challenges:
                chapter["perfected"] = True
            if self.chapter_index + 1 < len(save.md2.chapters):
                next_chapter = save.md2.chapters[self.chapter_index + 1]
                next_chapter["unlocked"] = True
            else:
                save.md3.unlocked = True
        save.md2.chapters[self.chapter_index] = chapter
        save.save()

        try:
            self.__close_audio_devices()
        except AttributeError:
            pass

        try:
            self.__metronome.playing = False
            self.__metronome.running = False
            self.__metronome.stop()
            self.__metronome.join()
        except RuntimeError:
            pass

        from ..main_menu import Menu

        self.change_state(Menu(self.screen, self.change_state))

    def __click_continue(self):
        self.__metronome.playing = False
        self.current_challenge += 1
        self.__vol_stream = []
        self.__played = []
        if self.current_challenge < self.num_challenges:
            self.__curr_rythm = self.__times[self.current_challenge] if not self.__use_pauses else self.__random_challenge()
            self.__finished_challenge = False
            self.__stream_processed = False
            self.__start_time = 0
            self.__started_challenge = False

    def __random_challenge(self):
        num_challenges_available = len(self.__times_with_pauses)
        index = np.random.randint(0, num_challenges_available)
        challenge = self.__times_with_pauses[index].copy()
        random.shuffle(self.__times_with_pauses[index])
        item: tuple[str, float]
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
        self.__times_with_pauses.pop(index)
        return challenge

    def __get_volume_stream(self):
        global vol
        self.__vol_stream.append(vol)

    def __start_audio_devices(self):
        def get_volume(indata, *_):
            global vol
            vol = round(np.linalg.norm(indata) * 10, 2)

        self.stream = sd.InputStream(callback=get_volume)
        self.stream.start()
        self.__vol_sensibility = self.__init_sensibility_button().on_click()

    def __close_audio_devices(self):
        try:
            self.stream.stop()
            self.stream.close()
        except AttributeError:
            pass

        try:
            self.__metronome.playing = False
            self.__metronome.running = False
            self.__metronome.stop()
            self.__metronome.join()
        except RuntimeError:
            pass

    def __init_sensibility_button(self):
        def callback():
            global vol
            self.__vol_sensibility = (vol * 1.2) if vol > 1.5 else 2

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

    def process_audio_stream(self):
        self.__played = []  # [(type, (start, length)), ...]
        mean_vol_threshold = 0
        if len(self.__vol_stream) > 0 and not np.isnan(self.__vol_stream).any() and not np.isinf(self.__vol_stream).any():
            mean_vol_threshold = np.mean(self.__vol_stream) * 0.7

        audio_stream = self.__vol_stream.copy()
        for i in range(len(audio_stream)):
            if audio_stream[i] < self.__vol_sensibility:
                audio_stream[i] = 0

        for i in range(2, len(self.__vol_stream) - 2):
            if self.__vol_stream[i] > mean_vol_threshold:
                self.__vol_stream[i] = np.mean(self.__vol_stream[i - 2:i + 3])

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

        self.__played = [("note", (start, start + length)) for start, length in threshold_meet]

        print("played nao processado", self.__played)
        for i, play in enumerate(self.__played[:-1]):
            next_play = self.__played[i + 1]
            if next_play[1][0] - play[1][1] >= 10 and play[0] == "note" and next_play[0] == "note":
                self.__played.insert(i + 1, ("pause", (play[1][1], next_play[1][0])))

        print("played depois da insercao das pausas", self.__played)

        i = 0
        while i < len(self.__played) - 1:
            if self.__played[i][0] == "pause" and self.__played[i + 1][0] == "pause":
                self.__played[i] = ("pause", (self.__played[i][1][0], self.__played[i + 1][1][1]))
                self.__played.pop(i + 1)
            elif self.__played[i][0] == "pause" and self.__played[i][1][1] - self.__played[i][1][0] <= 7:
                self.__played[i + 1] = (
                    self.__played[i + 1][0],
                    (
                        self.__played[i][1][0],
                        self.__played[i + 1][1][1]
                    )
                )
                self.__played.pop(i)
            else:
                i += 1
        print("played depois da juncao das pausas", self.__played)

        self.__stream_processed = True
        self.calculate_score()

    def calculate_score(self):
        correct_plays = 0
        for index, time in enumerate(self.__curr_rythm):
            if index >= len(self.__played):
                break
            played = self.__played[index][1][1] - self.__played[index][1][0]
            played_len = played / len(self.__vol_stream)
            played_type = self.__played[index][0]

            print(f"Time: {time}; Played: {played_len}; Diff: {abs(time[1] - played_len)}")
            if index == 0 or index == len(self.__curr_rythm) - 1:
                if time[1] - 0.2 <= played_len <= time[1] + 0.2 and time[0] == played_type:
                    correct_plays += 1
            else:
                if time[1] - 0.1 <= played_len <= time[1] + 0.1 and time[0] == played_type:
                    correct_plays += 1
        print(f"Correct plays: {correct_plays}; Score: {round(correct_plays / len(self.__curr_rythm), 2)}")
        print()
        self.score += round(correct_plays / len(self.__curr_rythm), 2)
