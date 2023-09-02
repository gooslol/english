# Copyright 2023 iiPython & DmmD GM

# Modules
import sys
import shlex
from pathlib import Path
from typing import Any, List, Union

# Initialization
__version__ = "0.0.5"

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
def parse_object(object: str) -> Any:
    chunks = object.split(" ")
    handlers = {
        "new": lambda: {"object": dict, "array": list}[chunks[1]](),
        "null": lambda: None, "true": lambda: True, "false": lambda: False
    }
    if chunks[0] in handlers:
        return handlers[chunks[0]]()

    elif object[0].isdigit() or object[0] in "+-.":
        object = float(object)
        return object if not object.is_integer() else int(object)

    elif (object[0] == "\"" and object[-1] == "\"") and (len(object) >= 2):
        return object[1:][:-1]

    return object

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

# Mainloop init
current_line, variables, jumped_prologue, stack = 0, {}, False, []

# Chapter builtins
def builtin_set(object: str, key: Union[str, int], value: Any) -> None:
    if object not in variables:
        return exit("english: no such object exists.")

    object = variables[object]
    if isinstance(object, list):
        if isinstance(key, str):
            return exit("english: an array does not have indexed keys.")

        # Ensure this list is padded enough for you to
        # index with whatever key we were given
        object += [None] * ((key or 1) - len(object))

    object[key] = value

builtin_chapters = {
    "print": lambda *a: print(*[variables.get(_, _) for _ in a]),
    "set": builtin_set
}

# Perform mainloop
while current_line < len(lines):
    line, content = lines[current_line], shlex.split(lines[current_line], posix = False)
    print(f"Line: {current_line + 1} | Content: {line} ({content})")

    # Match most built-in chapters
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

    # Handle the rest of the built-ins
    if content[0] in builtin_chapters:
        builtin_chapters[content[0]](
            *[parse_object(c)
            for c in content[1:]]
        )

    current_line += 1
