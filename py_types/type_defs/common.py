"""Common type families for ease-of-use."""

from .base import (
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


class SumType(metaclass=TypeFamily):
    """
    Base class for a union type.
    """
    type_members = [Any]

    def __init__(self, *args, **kwargs):
        if "type_members" in kwargs:
            self.type_members = kwargs["type_members"]
            self._registered_types = kwargs["type_members"]
        elif len(args) > 0:
            self.type_members = args
            self._registered_types = args
