"""Module for defining building blocks for type families.
Types built with these will return True for calls to isinstance()
whenever called with an argument that corresponds to their specified types.
Classes that inherit from others will automatically have their types extended."""

from abc import (
    ABCMeta,
)
from functools import (
    wraps,
)

def register(type_class):
    """Register a class to its given __registered_subclasses__
    Assumes that type_class is a child of some ABCMeta class,
    or otherwise has a .register method."""
    for subclass in type_class.__registered_subclasses__:
        type_class.register(subclass)


def typeclass(cl):
    """Class decorator to automatically call register() on a class."""
    register(cl)
    return cl


class TypeFamily(metaclass=ABCMeta):
    """
    Abstract base class for type families.
    Allows inheriting classes to set the class attribute "type_members",
    which will have the parents' _registered_types be extended with those in "type_members".
    reference: stackoverflow.com/questions/11675840/python-class-properties
    """

    def __new__(cls, name, bases, attrs):
        type_key = "type_members"
        types = []
        for base in bases:
            if base.has_key(type_key):
                types.extend(base[type_key])
        if attrs.has_key(type_key):
            types.extend(attrs[type_key])

        attrs["__registered_types__"] = types
        return type.__new__(cls, name, bases, attrs)

    @property
    def __registered_subclasses__(self):
        return self.__registered_types__

    @__registered_subclasses__.setter
    def __registered_subclasses__(self, val):
        self.__registered_types__ = val

    compare_to = isinstance
