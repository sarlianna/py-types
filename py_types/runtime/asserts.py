import functools
from collections import namedtuple

# ------------------
# type check
# ------------------


def typecheck(f):
    return _core_wrapper(f, _compare_types)


def _compare_types(f, name, arg):
    expected = f.__annotations__.get(name, None)
    if expected and not isinstance(arg, expected):
        raise TypeError("{} was expected to be of type {}, not {}".format(arg, expected, type(arg)))
    if name == "return" and expected is None and arg:
        raise TypeError("Expected no return, but got return {} of type {}".format(arg, type(arg)))


# -------------------
# custom validation
# -------------------


def validate(f):
    return _core_wrapper(f, _run_validator)


ValidationResult = namedtuple('ValidationResult', ['value', 'message'])


class ValidationError(BaseException):
    pass


def _run_validator(f, name, arg):
    validator = f.__annotations__.get(name, None)
    if validator is not None:
        result, reason = validator(arg)
        if not result:
            raise ValidationError("arg {} did not pass validation: {}".format(arg, reason))
    if name == "return" and validator is None and arg:
        raise ValidationError("Expected None but got a return value: {}".format(arg))


#---------------------
# core
#---------------------


def _core_wrapper(f, compare_f):

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        for i, arg in enumerate(args[:f.__code__.co_nlocals]):
            compare_f(f, f.__code__.co_varnames[i], arg)
        for name, arg in kwargs.items():
            compare_f(f, name, arg)

        result = f(*args, **kwargs)

        compare_f(f, 'return', result)
        return result
    return wrapper
