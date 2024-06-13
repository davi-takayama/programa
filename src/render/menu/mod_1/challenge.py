import re
import statistics
import time
from random import randint
from typing import List, Literal

import numpy as np
import pygame
import sounddevice as sd
from pygame import Surface
from pygame.event import Event

from src.utils.audioinput.audio_analyzer import AudioAnalyzer
from src.utils.audioinput.threading_helper import ProtectedList
from ....utils.button import Button
from ....utils.challenge_model import ChallengeBase
from ....utils.save_operations.read_save import Save

vol = 0
prev_vol = 0


class Challenge(ChallengeBase):
    def __init__(
            self,
            screen: Surface,
            change_state,
            chapter_index: int,
            use_audio: bool = False,
            num_challenges: int = 10,
            chromatic: bool = False,
            unlock_next: bool = True,
    ) -> None:
        super().__init__(screen, change_state, chapter_index, use_audio, num_challenges)
        self.staff_notes = ["E", "F", "G", "A", "B", "C", "D", "E", "F"]
        self.chromatic = chromatic
        self.current_note = self.pick_random_note()
        self._continue = False
        self.note_buttons: List[Button] = []
        self.continue_button = self.init_continue_button(self.click_continue)
        self.continue_text = ""
        self.played_notes = []
        self._queue = None
        self.stream = None
        self.analyzer = None
        if use_audio:
            self._queue = ProtectedList()
            self.start_audio_devices()
        else:
            self.init_note_buttons()
        self.level = self.regular_challenges if not use_audio else self.audio_challenges
        self.start_time = 0
        self.note_played = None
        self.end_button = self.init_end_button(self.click_end)
        self.event: callable = (
            self.handle_event_with_audio
            if use_audio
            else self.handle_event_without_audio
        )
        self.go_back_button = self.init_back_button(self.close_threads)
        self.vol_sensibility = 5
        self.sensibility_button = self.init_sensibility_button()
        self.continue_timer = 0
        self.unlock_next = unlock_next

    def render(self):
        if self.current_challenge == self.num_challenges:
            self.final_screen()
            self.end_button.render()
        else:
            self.level()
            self.go_back_button.render()
            self.render_challenge_info()

    def event_check(self, event_arg: Event):
        if self.current_challenge == self.num_challenges:
            self.end_button.event_check(event_arg)
        else:
            self.event(event_arg)
            self.go_back_button.event_check(event_arg)

        if event_arg.type == pygame.QUIT:
            try:
                self.close_threads()
            except AttributeError:
                pass

    def handle_event_without_audio(self, event):
        if not self._continue:
            for button in self.note_buttons:
                button.event_check(event)
        else:
            self.continue_button.event_check(event)

    def handle_event_with_audio(self, event):
        if self._continue:
            self.continue_button.event_check(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.continue_button.on_click()
        else:
            self.sensibility_button.event_check(event)

    def regular_challenges(self):
        self.screen.fill("white")
        self.staff.render()

        sharp = self.get_sharp_or_flat()

        self.note_renderer.quarter(
            x_pos=self.staff.trebble_cleff_asset.get_width() * 2 + 20,
            y_pos=(self.staff.c3_position - self.staff.note_spacing * 2) - (self.current_note[1] * self.staff.note_spacing),
            has_sharp=sharp
        )

        text = "Qual nota está sendo exibida?"
        width, _ = self.font.size(text)
        self.screen.blit(
            self.font.render(text, True, "black"),
            (
                (self.screen.get_width() // 2) - (width // 2),
                (self.screen.get_height() // 2),
            ),
        )

        if not self._continue:
            for button in self.note_buttons:
                button.render()
        else:
            text_width, text_height = self.font.size(self.continue_text)
            text_x = self.screen.get_width() // 2 - text_width // 2
            text_y = self.continue_button.pos[1] - text_height - 10
            self.screen.blit(
                self.font.render(self.continue_text, True, "black"),
                (text_x, text_y),
            )

            self.continue_button.render()

    def audio_challenges(self):
        self.screen.fill("white")
        self.staff.render()

        sharp = self.get_sharp_or_flat()

        self.note_renderer.quarter(
            x_pos=self.staff.trebble_cleff_asset.get_width() * 2 + 20,
            y_pos=(self.staff.c3_position - self.staff.note_spacing * 2) - self.current_note[1] * self.staff.note_spacing,
            has_sharp=sharp,
        )

        if self.note_played is None:
            text = "Use seu microfone para tocar a nota sendo exibida"
            width, _ = self.font.size(text)
            self.screen.blit(
                self.font.render(text, True, "black"),
                (
                    (self.screen.get_width() // 2) - (width // 2),
                    (self.screen.get_height() // 2),
                ),
            )
            self.get_note()
            self.sensibility_button.render()
        else:

            width, _ = self.font.size(self.continue_text)
            self.screen.blit(
                self.font.render(self.continue_text, True, "black"),
                (
                    (self.screen.get_width() // 2) - (width // 2),
                    ((self.screen.get_height() // 4) * 3),
                ),
            )
            self.continue_button.render()

            time_left = 3 - (pygame.time.get_ticks() - self.continue_timer) // 1000
            text = "continuando em X...".replace("X", str(time_left))
            width, _ = self.font.size(text)
            self.screen.blit(
                self.font.render(text, True, "black"),
                (
                    (self.screen.get_width() // 2) - (width // 2),
                    (self.screen.get_height() // 2),
                ),
            )

            if pygame.time.get_ticks() - self.continue_timer > 3000:
                self.continue_button.on_click()

    def get_sharp_or_flat(self):
        sharp: Literal['none', 'sharp', 'flat']
        if self.current_note[0].find("#") != -1:
            sharp = 'sharp'
        elif self.current_note[0].find("b") != -1:
            sharp = 'flat'
        else:
            sharp = 'none'
        return sharp

    def click_continue(self):
        self.current_note = self.pick_random_note()
        self._continue = False
        self.current_challenge += 1
        if self.note_played is not None:
            self.note_played = None
            self.played_notes = []

    def init_note_buttons(self):
        def check_answer(text: str):
            checked_value = self.current_note[0]
            checked_value = self.swap_note_if_invalid(checked_value)

            answ = text.split('/')
            if len(answ) > 1:
                if checked_value == answ[0] or checked_value == answ[1]:
                    self.score += 1
                    self.continue_text = "Correto!"
                    self.correct_se.play()
                else:
                    self.continue_text = ("Incorreto! A resposta correta era: " + checked_value)
                    self.incorrect_se.play()
            else:
                if text == checked_value:
                    self.score += 1
                    self.continue_text = "Correto!"
                    self.correct_se.play()
                else:
                    self.continue_text = ("Incorreto! A resposta correta era: " + checked_value)
                    self.incorrect_se.play()
            self._continue = True

        buttons = []
        notes = ["C", "D", "E", "F", "G", "A", "B"] if not self.chromatic else ["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G",
                                                                                  "G#/Ab", "A", "A#/Bb", "B"]

        for index, letter in enumerate(notes):
            button = Button(
                font=self.font,
                text=letter,
                on_click=lambda x=letter: check_answer(x),
                pos=(
                    (self.screen.get_width() // (len(notes) + 1) * (index + 1)) - self.font.size(letter)[0] // 2,
                    self.screen.get_height() // 4 * 3,
                ),
                screen=self.screen,
            )
            buttons.append(button)

        self.note_buttons = buttons

    def click_end(self):
        save = Save.load()
        chapter = save.md1.chapters[self.chapter_index]

        chapter["completed"] = self.score >= int(self.num_challenges * 0.7)
        chapter["perfected"] = self.score == self.num_challenges

        if self.chapter_index + 1 < len(save.md1.chapters):
            next_chapter = save.md1.chapters[self.chapter_index + 1]
            next_chapter["unlocked"] = True if self.unlock_next else next_chapter["unlocked"]
        else:
            save.md2.unlocked = True
        save.md1.chapters[self.chapter_index] = chapter
        save.save()
        from ..main_menu import Menu

        try:
            self.close_threads()
        except AttributeError:
            pass

        self.change_state(Menu(self.screen, self.change_state))

    def pick_random_note(self):
        num = randint(0, len(self.staff_notes) - 1)
        if self.chromatic:
            hassharp = randint(0, 2)
            return_char = ['', 'b', '#']
            return self.staff_notes[num] + return_char[hassharp], num
        else:
            return self.staff_notes[num], num

    def calc_note_position(self, note: str):
        note_name = note[0]
        has_sharp = note.find("#") != -1
        notes = ["E", "F", "G", "A", "B", "C", "D"]
        note_index = notes.index(note_name)
        pos = (
                self.staff.c3_position
                - (self.staff.note_spacing * note_index)
                - (self.staff.note_spacing * 2)
        )
        self.note_renderer.quarter(
            x_pos=self.staff.trebble_cleff_asset.get_width() * 3 + 20,
            y_pos=pos,
            has_sharp='sharp' if has_sharp else 'none',
            color="gray",
        )

    def get_note(self):
        end_time = time.time()
        global vol

        if self.note_played is None and vol > self.vol_sensibility and not self._continue:
            (
                self.calc_note_position(self.played_notes[-1])
                if self.played_notes
                else None
            )
            if self.start_time == 0:
                self.start_time = time.time()

            freq = self._queue.get()
            if freq is not None:
                note = self.analyzer.frequency_to_note_name(freq, 440)
                note_letter = re.sub(r"\d", "", note)
                self.played_notes.append(re.sub(r"\d", "", note_letter))
                self.calc_note_position(note)

            if end_time - self.start_time > 1 and self.start_time != 0:
                self.process_note_played()
        else:
            self.start_time = 0
            self.played_notes = []

    def process_note_played(self):
        self.note_played = statistics.mode(self.played_notes)
        self._continue = True
        checked_value = self.current_note[0]

        checked_value = self.swap_note_if_invalid(checked_value)
        note_equivalents: dict[str, str] = {"Cb": "B", "Db": "C#", "Eb": "D#", "Fb": "E", "Gb": "F#", "Ab": "G#", "Bb": "A#"}
        if checked_value in note_equivalents:
            checked_value = note_equivalents[checked_value]

        if self.note_played == checked_value:
            self.score += 1
            self.continue_text = "Correto!"
            self.correct_se.play()
        else:
            self.continue_text = (
                    "Incorreto! A nota correta era: "
                    + checked_value
                    + ". Você tocou: "
                    + self.note_played
            )
            self.incorrect_se.play()
        self.played_notes = []
        self.continue_timer = pygame.time.get_ticks()

    @staticmethod
    def swap_note_if_invalid(checked_value):
        if checked_value == 'E#':
            checked_value = 'F'
        elif checked_value == 'B#':
            checked_value = 'C'
        elif checked_value == 'Cb':
            checked_value = 'B'
        elif checked_value == 'Fb':
            checked_value = 'E'
        return checked_value

    def close_threads(self):
        try:
            self.stream.stop()
            self.stream.close()
            self.analyzer.stop()
            self.analyzer.join()
        except AttributeError:
            pass

    def start_audio_devices(self):
        def get_volume(indata, *_):
            volume_norm = np.linalg.norm(indata) * 10
            global prev_vol
            global vol
            prev_vol = vol
            vol = round(volume_norm, 2)

        self._queue = ProtectedList()
        self.analyzer = AudioAnalyzer(self._queue)
        self.analyzer.start()
        self.stream = sd.InputStream(callback=get_volume)
        self.stream.start()

    def init_sensibility_button(self):

        def callback():
            global vol
            self.vol_sensibility = (vol * 1.25) if vol > 1.5 else 2

        text = "Ajustar sensibilidade de volume"
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
