#!/usr/bin/env python3
import typing as t


CSI = '\033[1;'
RESET = '\033[0m'


def code_to_chars(code):
    if code == 0:
        return RESET
    return CSI + str(code) + 'm'


# class CodesName(object):
#     def __init__(self):
#         for name in dir(self):
#             if not name.startswith('_'):
#                 value = getattr(self, name)
#                 setattr(self, name, code_to_chars(value))


# class CodesID(object):
#     def __init__(self):
#         for name in dir(self):
#             if not name.startswith('_'):
#                 value = getattr(self, name)
#                 setattr(self, name, value)


class COLOR_ID:
    BLACK = 90
    RED = 91
    GREEN = 92
    YELLOW = 93
    BLUE = 34
    MAGENTA = 95
    CYAN = 96
    WHITE = 97
    RESET = 0
    END = 0


class BACK_COLOR_ID:
    BLACK = 40
    RED = 41
    GREEN = 42
    YELLOW = 43
    BLUE = 44
    MAGENTA = 45
    CYAN = 46
    WHITE = 47
    RESET = 0
    END = 0


class COLOR_NAME:
    BLACK = code_to_chars(30)
    RED = code_to_chars(31)
    GREEN = code_to_chars(32)
    YELLOW = code_to_chars(33)
    BLUE = code_to_chars(34)
    MAGENTA = code_to_chars(35)
    CYAN = code_to_chars(36)
    WHITE = code_to_chars(37)
    RESET = code_to_chars(0)
    END = code_to_chars(0)


class BACK_COLOR_NAME:
    BLACK = code_to_chars(40)
    RED = code_to_chars(41)
    GREEN = code_to_chars(42)
    YELLOW = code_to_chars(43)
    BLUE = code_to_chars(44)
    MAGENTA = code_to_chars(45)
    CYAN = code_to_chars(46)
    WHITE = code_to_chars(47)
    RESET = code_to_chars(0)
    END = code_to_chars(0)


def set_color_id(text, color_id):
    return RESET + code_to_chars(color_id) + str(text) + RESET


def set_color(text, *colors):

    return RESET + ''.join(colors) + str(text) + RESET


color_id = COLOR_ID()
color_name = COLOR_NAME()
bg_color_name = BACK_COLOR_NAME()
bg_color_id = BACK_COLOR_ID()


__all__ = [
    'color_id',
    'color_name',
    'bg_color_name',
    'bg_color_id',
    'set_color_id',
    'set_color',
]
