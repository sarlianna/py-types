"""Module for defining building blocks for type families.
Types built with these will return True for calls to isinstance()
whenever called with an argument that corresponds to their specified types.
Classes that inherit from others will automatically have their types extended."""

from collections.abc import (
    Callable
)
from copy import deepcopy


class TypeFamily(type):
    """
    Abstract base class for types/type families.
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


class ValidatedType(type):
    """
    Abstract base class for types that want to run custom validators on their members.
    inheritance through "type_members" is preserved, and inheritance of validators
    through "validators" is also in place.
    Validators are considered to be callables that return a bool.
    """

    def __new__(cls, name, bases, attrs):
        type_key = "type_members"
        validator_key = "validators"
        types = []
        validators = []
        for base in bases:
            types.extend(getattr(base, type_key, None))
            validators.extend(getattr(base, validator_key, None))
        if type_key in attrs:
            types.extend(attrs[type_key])
        if validator_key in attrs:
            validators.extend(attrs[validator_key])

        new_attrs = deepcopy(attrs)
        new_attrs["_registered_types"] = types
        new_attrs["_registered_validators"] = validators
        return super().__new__(cls, name, bases, new_attrs)

    def __instancecheck__(cls, instance):
        acceptable_types = tuple(cls._registered_types)
        if not isinstance(instance, acceptable_types):
            return False

        all_valid_validators = [validator for validator in cls._registered_validators if isinstance(validator, Callable)]
        all_pass = all([validator(instance) for validator in all_valid_validators])

        return all_pass


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
