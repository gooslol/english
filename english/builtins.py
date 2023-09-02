# Copyright 2023 iiPython & DmmD GM

# Modules
from typing import Any, List
from types import FunctionType

# Dataclasses
class Raw:
    pass

class Converted:
    pass

class Spacer(object):
    def __init__(self, text: str) -> None:
        self.text = text

# Main builtins handler
class EnglishBuiltins(object):
    def __init__(self) -> None:
        self.builtins = {}

    def builtin(self, takes_args: List[Converted | Spacer | Raw]) -> FunctionType:
        def internal(func: FunctionType):
            def callback_processor(*args) -> Any:
                new_args = []
                for index, arg_type in enumerate(takes_args):
                    if arg_type == Raw:
                        new_args.append(args[index][1])

                    elif (arg_type == Converted) and (args[index][0] is not None):
                        new_args.append(args[index][0])

                    elif (type(arg_type) == Spacer) and \
                         (arg_type.text != args[index][1]):
                        exit("english: improper transition word in sentence.")

                return func(*new_args)

            if not takes_args:
                def raw_processor(*args) -> None:
                    return func(*[a[0] for a in args])

                callback_processor = raw_processor  # noqa: F811

            self.builtins[func.__name__.split("_")[1]] = callback_processor

        return internal

# Pre-initialize class & export it
builtins = EnglishBuiltins()
