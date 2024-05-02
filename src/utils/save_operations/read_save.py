import json
import os
from dataclasses import dataclass
from typing import List

from .check_save import save_exists

_dir = os.path.dirname(__file__)[: __file__.index("src")]
save_path = os.path.join(_dir + "/savestate", "save.json")

if save_exists():
    data = json.load(open(save_path, "r"))
else:
    this_path = os.path.dirname(__file__)
    with open(this_path + "/save.json", "r") as file:
        data = json.load(file)


@dataclass
class Chapter:
    unlocked: bool
    completed: bool
    perfected: bool
    score: int


@dataclass
class Module:
    unlocked: bool
    chapters: List[Chapter]


@dataclass
class Save:
    md1: Module
    md2: Module
    md3: Module
    md4: Module

    @classmethod
    def load(cls):
        data = json.load(open(save_path, "r"))
        return cls(
            Module(**data["md1"]),
            Module(**data["md2"]),
            Module(**data["md3"]),
            Module(**data["md4"]),
        )

    def save(self):
        json.dump(
            {
                "md1": self.md1.__dict__,
                "md2": self.md2.__dict__,
                "md3": self.md3.__dict__,
                "md4": self.md4.__dict__,
            },
            open(save_path, "w"),
        )
