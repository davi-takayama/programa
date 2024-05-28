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

    def set_item(self, key, value):
        self.__dict__[key] = value


@dataclass
class Module:
    unlocked: bool
    chapters: List[Chapter]

    def __set_item__(self, key, value):
        self.__dict__[key] = value


@dataclass
class Save:
    md1: Module
    md2: Module
    md3: Module
    last_opened: int

    @classmethod
    def load(cls):
        with open(save_path, "r") as _file:
            save_data: dict = json.load(_file)
        return cls(
            Module(**save_data["md1"]),
            Module(**save_data["md2"]),
            Module(**save_data["md3"]),
            save_data["last_opened"],
        )

    def save(self):
        with open(save_path, "w") as __file:
            json.dump(
                {
                    "md1": self.md1.__dict__,
                    "md2": self.md2.__dict__,
                    "md3": self.md3.__dict__,
                    "last_opened": self.last_opened,
                },
                __file,
            )
