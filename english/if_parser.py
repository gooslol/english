# Copyright 2023 iiPython & DmmD GM

# Modules
from typing import Any, List, Tuple

# parse_if_data
def parse_if_data(content: List[str]) -> Tuple[str, str, str, str]:
    parsed, in_condition, payload = [], False, ""
    for item in content:
        if payload in [
            "is equal to",
            "is not equal to",
            "is less than",
            "is greater than"
        ]:
            in_condition = False
            parsed.append(payload)
            payload = ""

        if item == "is":
            parsed.append(payload)
            payload = item
            in_condition = True

        elif item == "then":
            parsed.append(payload)
            payload = ""

        elif in_condition:
            payload += " " + item

        else:
            payload += (" " + item if payload else item)

    data = parsed + [payload]
    return data[0], data[2], data[1], data[3]

# run_if_comp
def run_if_comp(value1: Any, value2: Any, condition: str) -> bool:
    return ((value1 == value2) and (condition == "is equal to")) or \
            ((value1 != value2) and (condition == "is not equal to")) or \
            ((value1 < value2) and (condition == "is less than")) or \
            ((value1 > value2) and (condition == "is greater than"))

