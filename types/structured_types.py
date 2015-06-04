"""Module for structured data types -- lists and dicts.
Defines type families that type check each of their members."""
from collections.abc import (
    Sequence,
)

from types.abc_types import (
    TypeFamily,
    typeclass,
)
from types.common_families import (
    Any,
)
from types.comparison import compare



@typeclass
class TypedSequence(metaclass=TypeFamily):
    """Enforces a type that is a sequence, with each element being a particular type.
    type_members is enforced on the actual sequence itself, and __restricted_to__ is enforced
    on each element.

    This class' compare_to always compares to Sequence, so you could probably leave type_members empty."""
    type_members = [Sequence]
    __restricted_to__ = None

    def __init__(self, *args, **kwargs):
        if "restricted_to" in kwargs:
            self.__restricted_to__ = kwargs["restricted_to"]
        elif len(args) > 0:
            self.__restricted_to__ = args[0]
        else:
            self.__restricted_to__ = Any

    @staticmethod
    def compare_to(value, intended):
        """Comparison method used by typechecker.
        Essentially replaces isinstance for values of this type.
        Assumes that intended is a TypedList instance."""
        if not isinstance(value, Sequence):
            return False
        acceptable_types = tuple(intended.__registered_types__)
        if not isinstance(value, acceptable_types):
            return False

        for val in value:
            if not compare(val, intended.__restricted_to__):
                return False

        return True


@typeclass
class TypedDict(metaclass=TypeFamily):
    """Enforces a dict where both keys and values are restricted to a particular type.
    type_members is enforced on the actual sequence itself,
    __keys_restricted_to__ is enforced on the keys,
    and __vals_restricted_To__ is enforced on the values.

    Note that all values are allowed to be a dictionary themselves, as long as their children
    also are instances of __keys_restricted_to__ and __vals_restricted_to__."""
    type_members = [dict]
    __keys_restricted_to__ = None
    __vals_restricted_to__ = None

    def __init__(self, *args, **kwargs):
        if "keys_restricted_to" in kwargs:
            self.__keys_restricted_to__ = kwargs["keys_restricted_to"]
        elif len(args) > 0:
            self.__keys_restricted_to__ = args[0]
        else:
            # should actually be only any hashable item
            self.__keys_restricted_to__ = Any

        if "vals_restricted_to" in kwargs:
            self.__vals_restricted_to__ = kwargs["vals_restricted_to"]
        elif len(args) > 1:
            self.__vals_restricted_to__ = args[1]
        else:
            self.__vals_restricted_to__ = Any

    @staticmethod
    def compare_to(value, intended):
        """Comparison method used by typechecker.
        Essentially replaces isinstance for values of this type.
        Assumes that intended is a TypedDict instance."""

        def walk_and_compare(current_key, current_val):
            if current_key and not compare(current_key, intended.__keys_restricted_to__):
                return False

            if not isinstance(current_val, dict):
                if not compare(current_val, intended.__vals_restricted_to__):
                    return False
                return True

            remaining = [walk_and_compare(key, value) for key, value in current_val.items()]
            return all(remaining)

        return walk_and_compare(None, value)
