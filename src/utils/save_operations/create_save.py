import os


def create_save():
    root_path = os.path.dirname(__file__)[: __file__.index("src")]
    this_path = os.path.dirname(__file__)
    if not os.path.exists(root_path + "savestate"):
        os.makedirs(root_path + "savestate")

        # open the file "save.josn" and copy it into the previously created folder
    with open(this_path + "/save.json", "r") as file:
        with open(root_path + "savestate/save.json", "w") as new_file:
            new_file.write(file.read())
