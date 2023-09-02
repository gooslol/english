# Copyright 2023 iiPython & DmmD GM

# Modules
import sys
import shlex
from pathlib import Path
from typing import Any, List

from . import __version__
from .simple_eval import SimpleEval
from .builtins import (
    builtins,
    Raw, Spacer, Converted
)
from .if_parser import parse_if_data, run_if_comp
from .exceptions import show_exception

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

filepath = Path(sys.argv[0])
if not filepath.is_file():
    exit("english: the specified file does not exist.")

# Load file
with open(filepath, "r") as fh:
    lines = fh.read().splitlines()

# Handle parsing
def cleanup_lines(source: List[str]) -> List[str]:
    return [
        line.lstrip()
        for line in lines
        if (not (line.startswith("btw") or line.startswith("by the way"))) \
            and line.strip()
    ]

# Parse chapters
lines, chapters = cleanup_lines(lines), {}
for line_number, line in enumerate(lines):
    data = line.split(" ")
    if data[0] != "chapter":
        continue

    chapters[data[1]] = line_number + 1

del line_number, line  # Get line number/line out of RAM

# Mainloop init
class EnglishInterpreter(object):
    def __init__(self) -> None:
        self.current_line = 0
        self.variables = {}
        self.has_jumped_prologue = False
        self.stack = []
        self.evaluator = SimpleEval()

    def parse_object(self, object: str) -> Any:
        chunks = object.split(" ")
        if chunks[0] == "new":
            return {"object": dict, "array": list}[chunks[1]]()

        try:
            return self.evaluator.eval(object, names = self.variables)

        except Exception:
            return None

    # Chapter builtins
    @builtins.builtin([Converted, Spacer("of"), Converted, Spacer("to"), Converted])
    def builtin_set(self, key: str | int, object: dict | list, value: Any) -> None:
        if isinstance(object, list):
            if isinstance(key, str):
                raise IndexError("arrays do not support object-like keys.")

            # Ensure this list is padded enough for you to
            # index with whatever key we were given
            object += [None] * ((key or 1) - len(object))

        object[key] = value

    @builtins.builtin([Converted, Spacer("from"), Converted, Spacer("as"), Raw])
    def builtin_get(self, key: str | int, object: dict | list, variable: str) -> None:
        self.variables[variable] = object[key]

    @builtins.builtin([])
    def builtin_print(*args) -> None:
        print(*args)

    def mainloop(self) -> None:
        last_if = None
        while self.current_line < len(lines):
            content = shlex.split(lines[self.current_line], posix = False)
            if content[0] not in ["if", "otherwise"]:
                last_if = None  # Reset the last if statement's value

            # Handle immediate built-ins
            def run_builtin(line_data: List[str]) -> None:
                builtins.builtins[line_data[0]](
                    *[(self.parse_object(c), c)
                    for c in line_data[1:]]
                )

            if content[0] in builtins.builtins:
                run_builtin(content)
                self.current_line += 1
                continue

            # Match more integrated chapters
            match content[0]:
                case "chapter":
                    if not self.has_jumped_prologue:
                        self.current_line = chapters.get("prologue")
                        if self.current_line is None:
                            exit(0)  # Graceful exit! Kachow!

                        self.has_jumped_prologue = True
                        continue

                case "jump":
                    match content[1]:
                        case "back":
                            last_stack = self.stack.pop()
                            if last_stack[1] == "epilogue":
                                exit(0)

                            self.current_line = last_stack[0]

                        case "last":
                            self.current_line = chapters[self.stack[-1][1]]
                        
                        case "to":
                            self.stack.append((self.current_line + 1, content[2]))
                            self.current_line = chapters.get(content[2])
                            if self.current_line is None:
                                if content[2] == "epilogue":
                                    exit(0)

                                raise ValueError(
                                    "cannot jump to a non-existant chapter.")

                        case _:
                            raise ValueError("you're trying to jump *where*?")

                case "if" | "otherwise":
                    if content[0] == "otherwise":
                        if last_if is None:
                            raise ValueError(
                                "otherwise must be used in conjunction with if.")

                        elif last_if is True:
                            self.current_line += 1
                            continue

                        elif content[1] != "if":
                            run_builtin(content[1:])
                            self.current_line += 1
                            continue

                        # Remove the otherwise and treat it like a regular if statement
                        content = content[1:]

                    try:
                        v1, v2, cond, expr = parse_if_data(content[1:])
                        last_if = run_if_comp(
                            self.parse_object(v1),
                            self.parse_object(v2),
                            cond
                        )
                        if last_if:
                            run_builtin(shlex.split(expr, posix = False))

                    except Exception as e:
                        raise TypeError(
                            "provided statement is unparsable."
                            if isinstance(e, IndexError) else
                            "statement is comparing uncomparable types."
                        )

                    self.current_line += 1
                    continue

            # Handle variable assignment
            if "is" in content:
                is_index, current = content.index("is"), self.variables
                if is_index > 1:
                    try:
                        for key in content[:(is_index - 1)]:
                            current = current[key.removesuffix("'s")]

                    except KeyError:
                        raise ValueError("provided item is missing ownership.")

                current[content[is_index - 1]] = \
                    self.parse_object(" ".join(content[is_index + 1:]))

            self.current_line += 1

# Handle CLI
if __name__ == "__main__":
    interpreter = EnglishInterpreter()
    try:
        interpreter.mainloop()

    except Exception as e:
        show_exception(e.args[0], interpreter.current_line, filepath)
