import os

from ..root_dir import root_dir


def save_exists() -> bool:
    _dir = root_dir
    save_path = os.path.join(_dir + "/savestate", "save.json")
    return os.path.isfile(save_path)
