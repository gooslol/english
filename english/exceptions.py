# Copyright 2023 iiPython & DmmD GM

# Modules
import sys
from pathlib import Path

from . import __version__

# Initialization
def show_exception(text: str, line: int, file: str) -> None:
    with open(Path(file), "r") as fh:
        lines = fh.read().splitlines()

    # Figure out what the line content is (10000 IQ play)
    line_track = 0
    for line_text in lines:
        if not line_text.strip() or \
             (line_text.startswith("btw") or line_text.startswith("by the way")):
            continue

        if line_track == line:
            break

        line_track += 1

    # Display error message
    python_version = ".".join([str(m) for m in sys.version_info[:3]])
    print(f"English v{__version__} - Running via Python {python_version}")
    print(f"Problem occured during execution of file '{file}':")
    print(f"  {line_track + 1} >  {line_text}\n")
    print(text)
