import json
import os
from dataclasses import dataclass
from typing import List

from .check_save_exists import save_exists
from ..root_dir import root_dir

_dir = root_dir
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
        save_data: object = json.load(open(save_path, "r"))
        return cls(
            Module(**save_data["md1"]),
            Module(**save_data["md2"]),
            Module(**save_data["md3"]),
            Module(**save_data["md4"]),
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
