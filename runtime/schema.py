""" Module designed to help ensure structured data is structured in a particular manner.
By using the schema decorator and passing a dictionary of keys and types as the annotation,
it validates that the given argument matches the structure of the annotation.

If an annotation is not a dictionary or iterable, it simply ignores it, allowing composition
with asserts.py's typecheck decorator."""

# TODO: Improve error messaging so it includes which key/value pair failed, as well as
# what it got for that pair and what it expected.

import functools
from collections import Iterable
import sys


def schema(function):
    """Check that a function's arguments match the given schemas."""

    @functools.wraps(function)
    def validated_function(*args, **kwargs):
        for i, arg in enumerate(args[:function.__code__.co_nlocals]):
            _validate_schema(function, function.__code__.co_varnames[i], arg)
        for name, arg in kwargs.items():
            _validate_schema(function, name, arg)

        result = function(*args, **kwargs)

        _validate_schema(function, 'return', result)
        return result

    return validated_function


def _validate_schema(f, name, arg):
    ann_schema = f.__annotations__.get(name, None)
    if ann_schema is not None:
        try:
            _format_asserts(ann_schema, arg)
        except Exception:
            error = TypeError("Schema did not successfully verify in function {} for argument '{}'.".format(f, name))
            error.__suppress_context__ = True
            tb = sys.exc_info()[2]
            raise error.with_traceback(tb)


def _format_asserts(form, data):
    """Checks that for each key value pair in form,
    there is a matching one in data where the value is the type
    specified in form."""
    # convert form to a list of tuples; ensure data is in an expected form
    try:
        form_items = form.items()
        assert isinstance(data, dict)
    except AttributeError:
        # str is an iterable, but we want to handle it here
        if not isinstance(form, Iterable) or isinstance(form, str):
            # here just checking a single item is enough.
            form_items = []
            assert isinstance(data, form)
        else:
            form_items = form
            assert isinstance(data, Iterable)

    for key, value in form_items:
        # test for absence of key (and if that's okay)
        if key not in data:
            try:
                assert isinstance(None, value)
            except TypeError:
                assert isinstance(None, type(value))
        elif isinstance(value, dict):
            assert isinstance(data[key], dict)
            _format_asserts(value, data[key])
        elif isinstance(value, list):
            assert isinstance(data[key], list)
            for item in data[key]:
                # Check that every item in data is the same as form_items' value[0].
                # Assumes a homogenous list -- data can't be different types.
                # Not sure how desirable that would be as a feature
                _format_asserts(value[0], item)
        else:
            assert key in data
            assert isinstance(data[key], value)

    return data
