"""Common type families for ease-of-use."""

from type_defs.base import (
    TypeFamily,
)

from collections.abc import (
    Sequence,
)


class Number(metaclass=TypeFamily):
    type_members = [int, float, complex]


class ArrayList(metaclass=TypeFamily):
    type_members = [list, bytes, bytearray, memoryview, Sequence]


class Any(metaclass=TypeFamily):
    type_members = [object]
