"""Module for more coherent function/callable types.

Instead of checking against collections.Callable, you can use these
for functions with arity/return type checks."""
from collections.abc import (
    Callable,
)

from .base import (
    TypeFamily,
)


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

        self.arity = arity
        self.return_type = return_type

    def __instancecheck__(self, instance):
        if not isinstance(instance, Callable):
            return False

        if not hasattr(instance, "__code__"):
            instance = instance.__call__
        f_code = instance.__code__

        if f_code.co_names:
            if not issubclass(f_code.co_names[0], self.return_type):
                return False
        if f_code.co_argcount != self.arity:
            return False

        return True

