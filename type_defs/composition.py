"""Methods to compose validators and types in different ways.
Unsure on current planned scope or usage for this, so work on it will probably be kept to a minimum.
"""

from ..runtime.asserts import (
    ValidationError,
)


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
    return f_and_g


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
        f_res = f(*args, **kwargs)
        g_res = g(*args, **kwargs)
        return (f_res, g_res)
    return f_and_g


def or_exc(f, g):
    """Ensures that one of f or g does not throw an exception on their arguments."""
    def f_or_g(*args, **kwargs):
        exc = False
        results = []
        for func in [f, g]:
            if not exc:
                try:
                    results.append(func(*args, **kwargs))
                except Exception:
                    exc = True

        if not exc:
            return tuple(results)
        else:
            return False
    return f_or_g
