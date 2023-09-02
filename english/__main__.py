# Copyright 2023 iiPython & DmmD GM

# Modules
import sys
import shlex
from pathlib import Path
from typing import Any, List

from .simple_eval import SimpleEval
from .builtins import (
    builtins,
    Raw, Spacer, Converted
)
from .if_parser import parse_if_data, run_if_comp

# Initialization
__version__ = "0.0.8"

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
current_line, variables, jumped_prologue, stack = 0, {}, False, []
evaluator = SimpleEval()

def parse_object(object: str) -> Any:
    chunks = object.split(" ")
    if chunks[0] == "new":
        return {"object": dict, "array": list}[chunks[1]]()

    try:
        return evaluator.eval(object, names = variables)

    except Exception:
        return None

# Chapter builtins
@builtins.builtin([Converted, Spacer("of"), Converted, Spacer("to"), Converted])
def builtin_set(key: str | int, object: dict | list, value: Any) -> None:
    if isinstance(object, list):
        if isinstance(key, str):
            return exit("english: an array does not have indexed keys.")

        # Ensure this list is padded enough for you to
        # index with whatever key we were given
        object += [None] * ((key or 1) - len(object))

    object[key] = value

@builtins.builtin([Converted, Spacer("from"), Converted, Spacer("as"), Raw])
def builtin_get(key: str | int, object: dict | list, variable: str) -> None:
    variables[variable] = object[key]

@builtins.builtin([])
def builtin_print(*args) -> None:
    print(*args)

# Perform mainloop
last_if = None
while current_line < len(lines):
    line, content = lines[current_line], shlex.split(lines[current_line], posix = False)

    # Clear the last if stack
    if content[0] not in ["if", "otherwise"]:
        last_if = None

    # Handle immediate built-ins
    def run_builtin(line_data: List[str]) -> None:
        builtins.builtins[line_data[0]](
            *[(parse_object(c), c)
            for c in line_data[1:]]
        )

    if content[0] in builtins.builtins:
        run_builtin(content)
        current_line += 1
        continue

    # Match more integrated chapters
    match content[0]:
        case "chapter":
            if not jumped_prologue:
                current_line = chapters.get("prologue")
                if current_line is None:
                    exit(0)  # Graceful exit! Kachow!

                jumped_prologue = True
                continue

        case "jump":
            match content[1]:
                case "back":
                    last_stack = stack.pop()
                    if last_stack[1] == "epilogue":
                        exit()

                    current_line = last_stack[0]

                case "last":
                    current_line = chapters[stack[-1][1]]
                
                case "to":
                    stack.append((current_line + 1, content[2]))
                    current_line = chapters.get(content[2])
                    if current_line is None:
                        exit(
                            "english: cannot jump into the backrooms."
                            if content[2] != "epilogue" else 0
                        )

                case _:
                    exit("english: are you high?")

        case "if" | "otherwise":
            if content[0] == "otherwise":
                if last_if is None:
                    exit("english: cannot use otherwise by itself.")

                elif last_if is True:
                    current_line += 1
                    continue

                elif content[1] != "if":
                    run_builtin(content[1:])
                    current_line += 1
                    continue

                # Remove the otherwise and treat it like a regular if statement
                content = content[1:]

            try:
                v1, v2, cond, expr = parse_if_data(content[1:])
                last_if = run_if_comp(parse_object(v1), parse_object(v2), cond)
                if last_if:
                    run_builtin(shlex.split(expr, posix = False))

            except IndexError:
                exit("english: invalid if statement")

            except TypeError:
                exit("english: statement is comparing uncomparable types")

            current_line += 1
            continue

    # Handle variable assignment
    if "is" in content:
        is_index, current = content.index("is"), variables
        if is_index > 1:
            try:
                for key in content[:(is_index - 1)]:
                    current = current[key.removesuffix("'s")]

            except KeyError:
                exit("english: grammatical ownership problem")

        current[content[is_index - 1]] = parse_object(" ".join(content[is_index + 1:]))

    current_line += 1
