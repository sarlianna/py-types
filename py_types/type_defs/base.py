"""Module for defining building blocks for type families.
Types built with these will return True for calls to isinstance()
whenever called with an argument that corresponds to their specified types.
Classes that inherit from others will automatically have their types extended."""

from collections.abc import (
    Callable
)
from copy import deepcopy


def can_check_isinstance(specified_type):
    """Checks that specified_type can be the second arg to isinstance without raising an exception."""
    try:
        isinstance(5, specified_type)
    except TypeError:
        return False
    return True


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
            types.extend(getattr(base, type_key, []))
        if type_key in attrs:
            types.extend(attrs[type_key])

        for ty in types:
            if not can_check_isinstance(ty):
                raise TypeError("Expected a type <class 'type'> for all validated_types but got value {} of type {}.".format(ty, type(ty)))
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
            types.extend(getattr(base, type_key, []))
            validators.extend(getattr(base, validator_key, []))
        if type_key in attrs:
            types.extend(attrs[type_key])
        if validator_key in attrs:
            validators.extend(attrs[validator_key])

        for ty in types:
            if not can_check_isinstance(ty):
                raise TypeError("Expected a type <class 'type'> for all validated_types but got value {} of type {}.".format(ty, type(ty)))
        for va in validators:
            if not isinstance(va, Callable):
                raise TypeError("Expected a Callable for all validators, but instead got value {} of type {}.".format(va, type(va)))

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
