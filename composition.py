import functools
import abc
from asserts.asserts import (
    ValidationError,
    ValidationResult,
)
from collections import Callable

# TODO: nothing has a consistent interface or consistent way of working with them.
# thus, we need to have custom comparison methods to call and use that abstract away the differences.
# CORE CHANGES NEEDED

# -----------------------
# Type composition functions
# -----------------------


def or_comp(*types):
    """Returns a value that can be called with isinstance to determine if the value is any of the types given in args"""
    # isinstance accepts a tuple of objects, so we just make a tuple of the list.
    return tuple(types)


def and_val(f, g):
    def f_and_g(value):
        f_result = f(value)
        g_result = g(value)
        if not (f_result and g_result):
            raise ValidationError("""Joint validator -- AND composition failed with validators {f} and {g}.
  Value passed: {actual}
  Validator results: {f} - {f_res}
                     {g} - {g_res}""".format(f=f, g=g, actual=value, f_res=f_result, g_res=g_result))
        return (f_result and g_result)
    return f_or_g


def or_val(f, g):
    """Ensures that at least one of f and g returns True on the same arguments, or throws an exception.
    If f returns True, does not execute g."""
    def f_or_g(value):
        f_result = f(value)
        if not f_result[0]:
            g_result = g(value)
            if not g_result[0]:
                raise ValidationError("""Joint validator -- OR composition failed with types {f} and {g}.
  Returns with argument {value}:
    {f}: {f_res}
    {g}: {g_res}""".format(f=f, g=g, f_res=f_result, g_res=g_result, value=value))
        if f_result[0]:
            result = f_result
        else:
            result = g_result
        return result
    return f_or_g


def and_exc(f, g):
    """Ensures that neither f nor g throws an exception on their arguments."""
    # if they throw an exception then just let it pass.
    def f_and_g(*args, **kwargs):
        f(*args, **kwargs)
        g(*args, **kwargs)
        return True
    return f_and_g


def or_exc(f, g):
    """Ensures that one of f or g does not throw an exception on their arguments."""
    def f_or_g(*args, **kwargs):
        exc = False
        for func in [f, g]:
            if not exc:
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    exc = True

        if not exc:
            return True
        else:
            return False
    return f_or_g


# ------------------------
# Type abstractions
# ------------------------

def JointType(*types):
    return or_comp(types)


# TODO: currently this has to be called with @validate, not @typecheck
# @validate should be changed to handle this, because I can't find a way to represent this
# as an isinstance()-able class.
# this is really inconsistent, ugh
class IntersectionType(object):
    def __init__(self, *args):
        self.types = args

    def __call__(self, value):
        failed = False

        for t in self.types:
            # please no
            if not isinstance(value, t) and not (isinstance(t, Callable) and t(value)):
                failed = True
                break
        if failed:
            reason = """value was not subclass of all expected types:
      Types: {}
      value's type: {}""".format(self.types, type(value))
        else:
            reason = None
        return (not failed, reason)


class JointValidation(object):
    def __init__(self, *args):
        self.types = args

    def __call__(self, value):
        type_check = functools.reduce(or_val, self.types)
        return type_check(value)
