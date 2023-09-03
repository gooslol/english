# Copyright 2023 iiPython & DmmD GM

# Modules
import re
import sys
from pathlib import Path
from typing import Any, List

from . import __version__
from .builtins import (
    builtins, Argument
)
from .simple_eval import SimpleEval

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
        self.line_pattern = re.compile(r"(?:(\".*?\")|(\S+))")
        self.variables = {}

        self._default_datatypes = {
            "null": None, "true": True, "false": False
        }
        self._evaluator = SimpleEval()

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

    def eval_expr(self, expr: str) -> Any:
        parsed_value = self.parse_line([expr])
        if (len(parsed_value) > 1) or parsed_value[0].raw == parsed_value[0].obj:
            return self._evaluator.eval(expr, names = self.variables)

        return parsed_value[0].obj

    def exec_line(self, line: List[str]) -> None:
        print(f"Line: {self.line} | Content: {line}")
        builtin = builtins.get(line[0])
        if builtin is not None:
            return builtin(self, *self.parse_line(line[1:]))

        elif "is" in line:
            index, item = line.index("is"), self.variables
            for object in line[:index - 1]:
                item = item[object.removesuffix("'s")]

            item[line[index - 1]] = self.eval_expr(" ".join(line[index + 1:]))

    def parse_line(self, line: List[str]) -> List[Argument]:
        new_line = []
        for chunk in line:
            if chunk[0] == "\"" and chunk[-1] == "\"":
                new_line.append(Argument(chunk, chunk[1:][:-1]))

            elif chunk[0] in "+-" or chunk[0].isdigit() or "." in chunk:
                new_line.append(Argument(chunk,
                    (float if "." in chunk else int)(chunk)
                ))

            elif chunk in self._default_datatypes:
                new_line.append(Argument(chunk, self._default_datatypes[chunk]))

            else:
                new_line.append(Argument(chunk, self.variables.get(chunk, chunk)))

        return new_line

    def main_loop(self) -> None:
        while self.line < self.line_count:
            line_content = self.split_line(self.lines[self.line])
            self.exec_line(line_content)
            self.line += 1

# Handle CLI
if __name__ == "__main__":
    english = English()
    english.load_file(sys.argv[0])
    english.main_loop()
