# Copyright 2023 iiPython
# Copyright 2023 DmmD GM

# Modules
import sys
import shlex
from pathlib import Path
from typing import Any, List

# Initialization
__version__ = "0.0.3"

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
    data = object.split(" ")
    if data[0] == "new":
        return {"object": dict, "array": list}[data[1]]()

    bool_obj = {"true": True, "false": False}.get(object)
    if bool_obj is not None:
        return bool_obj

    elif object[0].isdigit() or object[0] in "+-.":
        object = float(object)
        return object if not object.is_integer() else int(object)

    elif (object[0] == "\"" and object[-1] == "\"") and (len(object) >= 2):
        return object[1:][:-1]

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

# Perform mainloop
current_line, variables, jumped_prologue, stack = 0, {"goos": {}}, False, []
while current_line < len(lines):
    line, content = lines[current_line], shlex.split(lines[current_line], posix = False)

    # If we hit a chapter, skip to prologue
    # This ASSUMES that we already executed all topmost code
    if content[0] == "chapter":
        if jumped_prologue:
            current_line += 1
            continue

        current_line = chapters.get("prologue")
        if current_line is None:
            exit(0)  # Graceful exit! Kachow!

        jumped_prologue = True
        continue

    # Handle jumping
    if content[0] == "jump":
        if content[1] == "back":
            current_line = stack.pop()[0]
            continue

        elif content[1] == "last":
            current_line = chapters[stack[-1][1]]
            continue

        elif content[1] != "to":
            exit("english: are you high?")

        # Handle jumping to new chapter
        stack.append((current_line + 1, content[2]))
        current_line = chapters.get(content[2])
        if current_line is None:
            exit("english: cannot jump into the backrooms.")

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

    # Debug info! Wooo!!
    print(f"Line: {current_line} | Content: {line} ({content})")
    print(variables)
    current_line += 1
