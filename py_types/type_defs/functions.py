"""Module for more coherent function/callable types.

Instead of checking against collections.Callable, you can use these
for functions with arity/return type checks."""
from collections import (
    Callable,
)

from .base import (
    TypeFamily,
)


def can_check_isinstance(specified_type):
    """Checks that specified_type can be the second arg to isinstance without raising an exception."""
    try:
        isinstance(5, specified_type)
    except TypeError:
        return False
    return True


class Function(metaclass=TypeFamily):
    """Enforces a type that's a function, has a specific number of arguments,
    and returns a specific type.

    Pass arity, return_type to the init() call.  Arity is assumed to include only
        the number of arguments that are explicity in the function's definition.
        if your function takes only *args, **kwargs, and extracts 4 values from them,
        you should consider it to have an arity of 2.
    return_type is compared directly with the return annotation. If there is no annotation,
        it skips the check (since gradual typing is a goal)."""
    type_members = [Callable]

    def __init__(self, *args, **kwargs):
        if len(args) >= 1:
            arity = args[0]
        elif "arity" in kwargs:
            arity = kwargs["arity"]

        if len(args) >= 2:
            return_type = args[1]
        elif "return_type" in kwargs:
            return_type = kwargs["return_type"]

        if arity not in range(0, 30):
            raise ValueError("Invalid arity for a function.  Expected a value in [0, 30), but got value {}.".format(arity))
        if not can_check_isinstance(return_type):
            raise TypeError("Need a type to check return value against, not a value:\n\t"
                            + "Expected a value of type <class 'type'> but got type {}.".format(type(return_type)))

        self.arity = arity
        self.return_type = return_type

    def __instancecheck__(self, instance):
        if not isinstance(instance, Callable):
            return False

        if "return" in instance.__annotations__:
            if not issubclass(instance.__annotations__["return"], self.return_type):
                return False

        if not hasattr(instance, "__code__"):
            instance = instance.__call__
        f_code = instance.__code__

        if f_code.co_argcount != self.arity:
            return False

        return True

