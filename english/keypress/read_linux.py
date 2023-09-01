# Copyright 2023 iiPython

# Modules
import sys
import tty
import termios
from typing import Union

from . import keys

# Initialization
keymap = {
    "[D": keys.LEFT,
    "[C": keys.RIGHT,
    "[A": keys.UP,
    "[B": keys.DOWN,
    "\r": keys.ENTER,
    "\x7f": keys.BACKSPACE,
    "\x03": keys.CTRL_C
}

# Linux-based readchar
def readchar() -> Union[str, int]:
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            ch = sys.stdin.read(2)
            if ch in keymap:
                return keymap[ch]

        elif ch in keymap:
            return keymap[ch]

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return ch
