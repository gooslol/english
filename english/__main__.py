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
        self.stack, self.comp_stack, self.variables = [], [], {}

        self._default_datatypes = {
            "null": None, "true": True, "false": False
        }
        self._evaluator = SimpleEval()

    def load_file(self, path: str) -> None:
        if not Path(path).is_file():
            exit("english: specified file does not exist.")

        with open(path, "r") as fh:
            self.lines = [
                ln.lstrip() for ln in fh.read().splitlines()
                if not (ln.startswith(("btw", "by the way")) or not ln.strip())
            ]
            self.ran_prologue = False
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
        if parsed_value[0].raw.startswith("new "):
            return {"array": list, "object": dict}[parsed_value[0].raw.split(" ")[1]]()

        elif (len(parsed_value) > 1) or parsed_value[0].raw == parsed_value[0].obj:
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

            elif ((chunk[0] in "+-" and len(chunk) > 1) or chunk[0].isdigit() or \
                "." in chunk) and " " not in chunk:
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
            if line_content[0] == "chapter":
                prologue_line = self.chapters.get("prologue")
                if prologue_line is None:
                    return exit(0)

                self.line = prologue_line if not self.ran_prologue else self.line + 1
                continue

            self.exec_line(line_content)
            self.line += 1

# Handle CLI
if __name__ == "__main__":
    english = English()
    english.load_file(sys.argv[0])
    try:
        english.main_loop()

    except Exception as e:
        with open(Path(sys.argv[0]), "r") as fh:
            line_contents = fh.read().splitlines()

        # Calculate actual file line based on the virtual one
        virt_line = 0
        for line_number, line in enumerate(line_contents):
            if line.startswith(("btw", "by the way")) or not line.strip():
                continue

            elif virt_line == english.line:
                break

            virt_line += 1

        # Handle some terminal info
        def escape(code: str) -> str:
            return f"\x1b[{code}m"

        red, reset = escape("38;5;196"), escape("0")
        python_version = ".".join([str(c) for c in sys.version_info[:3]])
        print(f"English v{__version__} running via {python_version}")
        print(f"Problem occured while running file '{sys.argv[0]}':")
        print(f"  {line_number + 1} >  {line}")
        print(f"  {' ' * len(str(line_number + 1))}    {red}{'^' * len(line)}{reset}")
        print(f"\nProblem: {e}")
