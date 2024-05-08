from pygame import Surface

from src.render.staff import Staff
from src.utils.renderable import Renderable


class Challenge(Renderable):
    def __init__(self, screen: Surface, change_state, chapter_index: int, use_audio: bool = False, num_challenges: int = 10, ):
        super().__init__(screen, change_state)
        self.screen = screen
        self.change_state = change_state
        self.chapter_index = chapter_index
        self.use_audio = use_audio
        self.num_challenges = num_challenges
        self.__staff = Staff(screen, self.screen.get_height() // 3, (4, 4))
        self.__continue = False
