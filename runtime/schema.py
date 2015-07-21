""" Module designed to help ensure structured data is structured in a particular manner.
By using the schema decorator and passing a dictionary of keys and types as the annotation,
it validates that the given argument matches the structure of the annotation.

If an annotation is not a dictionary or iterable, it simply ignores it, allowing composition
with asserts.py's typecheck decorator.

ON NESTED LIST SCHEMAS:
Nested list schemas have been added, but please note all of the following pitfalls with the current implementation:
- due to common usage of a tuple of types with isinstance, tuples in a schema are treated as a single value.
    (i.e. the entire tuple is passed to isinstance.) If you would actually like for the decorator to check
    for a sequence of items corresponding to the types given, please use a list.
    If you do use a list, it will allow the actual value to be a tuple.

- The code currently checks only for isinstance(schema_type, list) for a list of types/schemas to check.
    Other Iterable type objects will be ignored unless they return true for isinstance(instance, list)

- The code for checking a schema list _is_ dependent on order.  The order of the arguments must match the order declared
    in the schema.  This seems generally desirable to me at the moment, but note that there is no alternative."""

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
            print(sys.exc_info())
            tb = sys.exc_info()[2]
            raise error.with_traceback(tb)


def _format_asserts(form, data):
    """Checks that for each key value pair in form,
    there is a matching one in data where the value is the type
    specified in form."""
    # convert form to a list of tuples; ensure data is in an expected form
    is_dict = True
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
            if len(form) == 1:
                for item in data:
                    _format_asserts(form[0], item)
                return
            else:
                is_dict = False

    if is_dict:
        _check_values_dict(form_items, data)
    else:
        _check_values_list(form_items, data)

    return data


def _check_values_dict(form_items, data):
    """Comparison logic for dictionary schemas.
    Checks the key exists in the data,
    Recurses on dicts and lists,
    and otherwise just checks the value to the form_item's value via isinstance."""
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
            assert isinstance(data[key], (list, tuple))
            if len(data[key]) == 1:
                for item in data[key]:
                    # Check that every item in data is the same as form_items' value[0].
                    # Assumes a homogenous list -- data can't be different types.
                    # Not sure how desirable that would be as a feature
                    _format_asserts(value[0], item)
            else:
                _format_asserts(value, data[key])
        else:
            assert key in data
            assert isinstance(data[key], value)


def _check_values_list(form_items, data):
    """Comparison logic for list schemas.
    Recurses on dicts and list, otherwise just compares the value via isinstance.
    Mostly looks exactly like the dict code but uses indexes instead of keys.  May be worth combining them!

    Note: this logic is sensitive to ordering!
        If you have implemented an iterable that does not return a consistent iteration order,
        there may be issues with this code.
        I'd like to remove this restriction in the future, but considering the main use case
        is testing against lists of dictionary schemas, checking in an order-agnostic way seems
        expensive and complicated.

    Second Note: this code is never used unless the schema specifies a list of more than one element, i.e.
        non-homogenous lists. The dict code handles nested lists that are only one element long itself.
        one-element lists are assumed to match lists of any size,
        as long as their members validate against the schema's only member."""
    assert len(data) == len(form_items)
    for index, value in enumerate(form_items):
        if isinstance(value, dict):
            assert isinstance(data[index], dict)
            _format_asserts(value, data[index])
        if isinstance(value, list):
            assert isinstance(data[index], (list, tuple))
            if len(data[index]) == 1:
                for item in data[index]:
                    _format_asserts(value[0], item)
            else:
                _format_asserts(value, data[index])
        else:
            assert isinstance(data[index], value)
