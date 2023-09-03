# Copyright 2023 iiPython & DmmD GM

# Modules
import re
import sys
from typing import List
from pathlib import Path

from . import __version__
from .builtins import (
    builtins, Argument
)

# Initialization
sys.argv = sys.argv[1:]
if not sys.argv:
    exit("\n".join([line.split(" ~ ")[1] for line in f"""
    ~ English (v{__version__}) Interpreter
    ~ (c) 2023 iiPython; (c) 2023 DmmD GM
    ~ 
    ~ Usage:
    ~     english <file>
    ~ 
    ~ See docs/ for more detailed information.""".splitlines()[1:]]))

# Main class
class English(object):
    def __init__(self) -> None:
        self.line = 0
        self.line_pattern = re.compile(r"(?:\"(.*?)\"|(\S+))")
        self._default_datatypes = {
            "null": None, "true": True, "false": False
        }

    def load_file(self, path: str) -> None:
        if not Path(path).is_file():
            exit("english: specified file does not exist.")

        with open(path, "r") as fh:
            self.lines = [
                ln for ln in fh.read().splitlines()
                if (not (ln.startswith("btw") or ln.startswith("by the way"))) and \
                    ln.strip()
            ]
            self.line_count = len(self.lines)
            self.chapters = {
                ln.split(" ")[1]: idx + 1
                for idx, ln in enumerate(self.lines) if ln.startswith("chapter ")
            }

    def split_line(self, line: str) -> List[str]:
        objects = self.line_pattern.findall(line)
        return [obj[0] or obj[1] for obj in objects]

    def exec_line(self, line: List[Argument]) -> None:
        # print(f"Line: {self.line} | Content: {line}")
        builtins[line[0].raw](self, *line[1:])

    def parse_line(self, line: List[str]) -> List[Argument]:
        new_line = []
        for chunk in line:
            if chunk[0] == "\"" and chunk[-1] == "\"":
                new_line.append(Argument(chunk, chunk[1:][:-1]))

            elif chunk[0] in "+-." or chunk[0].isdigit():
                new_line.append(Argument(chunk,
                    (float if chunk[0] == "." else int)(chunk)
                ))

            elif chunk in self._default_datatypes:
                new_line.append(Argument(chunk, self._default_datatypes[chunk]))

            else:
                new_line.append(Argument(chunk, chunk))

        return new_line

    def main_loop(self) -> None:
        while self.line < self.line_count:
            line_content = self.split_line(self.lines[self.line])
            self.exec_line(self.parse_line(line_content))
            self.line += 1

# Handle CLI
if __name__ == "__main__":
    english = English()
    english.load_file(sys.argv[0])
    english.main_loop()
