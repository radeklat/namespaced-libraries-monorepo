import os
import shutil
from pathlib import Path


class ProjectInfo:
    source_directory: Path = Path("src")
    namespace_directory: Path = source_directory / "company_utils"


PROJECT_INFO = ProjectInfo()
_HEADER_LEVEL_CHARACTERS = {1: "#", 2: "=", 3: "-"}


def print_header(text: str, level: int = 1, icon: str = ""):
    if icon:
        icon += " "

    padding_character = _HEADER_LEVEL_CHARACTERS[level]
    if os.getenv("CIRCLECI", ""):
        padding_length = 80
    else:
        padding_length = max(shutil.get_terminal_size((80, 20)).columns - (len(icon) * 2), 0)

    padding = f"\n{{:{padding_character}^{padding_length}}}\n"
    if level == 1:
        text = text.upper()
    print(padding.format(f" {icon}{text} {icon}"))
