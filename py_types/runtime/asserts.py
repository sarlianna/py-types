import functools
from collections import namedtuple

# ------------------
# type check
# ------------------


def typecheck(f):

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        print("in typecheck wrapper")
        for i, arg in enumerate(args[:f.__code__.co_nlocals]):
            _compare_types(f, f.__code__.co_varnames[i], arg)
        for name, arg in kwargs.items():
            _compare_types(f, name, arg)

        result = f(*args, **kwargs)

        _compare_types(f, 'return', result)
        return result
    return wrapper


def _compare_types(f, name, arg):
    expected = f.__annotations__.get(name, None)
    # If the annotation isn't a type (a class), just don't check it.
    # Done to allow inter-op with other decorators using annotations.
    if type(expected) not in [type, type(None)]:
        return

    if name == "return" and (expected is type(None) or expected is None) and arg:
        raise TypeError("\n    In {}:\n\texpected no return value \n\tbut got return value {} of type {}".format(f, arg, type(arg)))
    if expected and not isinstance(arg, expected):
        if name == "return":
            desc = "expected a return type of {},".format(expected)
        else:
            desc = "expected argument '{}' to have type {},".format(name, expected)
        raise TypeError("\n    In {}:\n\t{}\n\tbut instead got value '{}' with type {}.".format(f, desc, arg, type(arg)))
