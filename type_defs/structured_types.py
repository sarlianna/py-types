"""Module for structured data types -- lists and dicts.
Defines type families that type check each of their members."""
from collections.abc import (
    Sequence,
)

from type_defs.base import (
    TypeFamily,
)
from type_defs.common import (
    Any,
)


class TypedSequence(metaclass=TypeFamily):
    """Enforces a type that is a sequence, with each element being a particular type.
    type_members is enforced on the actual sequence itself, and __restricted_to__ is enforced
    on each element.

    This class' compare_to always compares to Sequence, so you could probably leave type_members empty."""
    type_members = [Sequence]
    _restricted_to = None

    def __init__(self, *args, **kwargs):
        if "restricted_to" in kwargs:
            self._restricted_to = kwargs["restricted_to"]
        elif len(args) > 0:
            self._restricted_to = args[0]
        else:
            self._restricted_to = Any

    def __instancecheck__(self, instance):
        """Ensure that instance is a sequence, instance is one of self.type_members,
        and that each member is one of self._restricted_to."""
        if not isinstance(instance, Sequence):
            return False

        acceptable_types = tuple(self._registered_types)
        if not isinstance(instance, acceptable_types):
            return False

        are_values_valid = all([isinstance(value, self._restricted_to) for value in instance])

        return are_values_valid


class TypedDict(metaclass=TypeFamily):
    """Enforces a dict where both keys and values are restricted to a particular type.
    type_members is enforced on the actual sequence itself,
    __keys_restricted_to__ is enforced on the keys,
    and __vals_restricted_To__ is enforced on the values.

    Note that all values are allowed to be a dictionary themselves, as long as their children
    also are instances of __keys_restricted_to__ and __vals_restricted_to__."""
    type_members = [dict]
    _keys_restricted_to = None
    _vals_restricted_to = None

    def __init__(self, *args, **kwargs):
        if "keys_restricted_to" in kwargs:
            self._keys_restricted_to = kwargs["keys_restricted_to"]
        elif len(args) > 0:
            self._keys_restricted_to = args[0]
        else:
            # should actually be only any hashable item
            self._keys_restricted_to = Any

        if "vals_restricted_to" in kwargs:
            self._vals_restricted_to = kwargs["vals_restricted_to"]
        elif len(args) > 1:
            self._vals_restricted_to = args[1]
        else:
            self._vals_restricted_to = Any

    def __instancecheck__(self, instance):
        def walk_and_compare(current_key, current_val):
            """recursively walk the dict, checking that each key is one of _keys_restricted_to
            and that each value is either a dict or one of _vals_restricted_to"""
            if current_key and not isinstance(current_key, self._keys_restricted_to):
                return False

            if not isinstance(current_val, dict):
                if not isinstance(current_val, self._vals_restricted_to):
                    return False
                return True

            remaining = [walk_and_compare(key, value) for key, value in current_val.items()]
            return all(remaining)

        return walk_and_compare(None, instance)
