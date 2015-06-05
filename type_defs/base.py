"""Module for defining building blocks for type families.
Types built with these will return True for calls to isinstance()
whenever called with an argument that corresponds to their specified types.
Classes that inherit from others will automatically have their types extended."""

from functools import (
    wraps,
)
from collections.abc import (
    Iterable,
)
from copy import deepcopy


class TypeFamily(type):
    """
    Abstract base class for type families.
    Allows inheriting classes to set the class attribute "type_members",
    which will have the parents' _registered_types be extended with those in "type_members".
    This in turn gets set to the current class' _registered_types, which is used by the
    isinstance override.
    """

    def __new__(cls, name, bases, attrs):
        type_key = "type_members"
        types = []
        for base in bases:
            types.extend(getattr(base, type_key, None))
        if type_key in attrs:
            types.extend(attrs[type_key])

        new_attrs = deepcopy(attrs)
        new_attrs["_registered_types"] = types
        return super().__new__(cls, name, bases, new_attrs)

    def __instancecheck__(cls, instance):
        acceptable_types = tuple(cls._registered_types)
        return isinstance(instance, acceptable_types)
