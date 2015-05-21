"""Common type families for ease-of-use."""

from abc_types import (
    TypeFamily,
    typeclass,
)

from collections.abc import (
    Sequence,
)


@typeclass
class Number(metaclass=TypeFamily):
    type_members = [int, float, complex]


@typeclass
class ArrayList(metaclass=TypeFamily):
    type_members = [list, bytes, bytearray, memoryview, Sequence]

