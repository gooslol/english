# Copyright 2023 iiPython

# Modules
import string
import msvcrt
from typing import Union

from . import keys

# Initialization
string_check = string.ascii_letters + string.digits + string.punctuation

# Main function
def readchar() -> Union[str, int]:
    ch = msvcrt.getch()
    ch_dc = ch.decode("mbcs")
    if ch_dc in string_check:
        return ch_dc

    ch = ord(ch)
    if ch == 0 or ch == 224:
        ch = ord(msvcrt.getch())

    return ch if ch != keys.SPACE else " "
