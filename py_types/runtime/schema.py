""" Module designed to help ensure structured data is structured in a particular manner.
By using the schema decorator and passing a dictionary of keys and types as the annotation,
it validates that the given argument matches the structure of the annotation.

If an annotation is not a dictionary or iterable, it simply ignores it, allowing composition
with asserts.py's typecheck decorator.

ON NESTED LIST SCHEMAS:
These are full of odd pitfalls at the moment.
Currently known possible pitfalls:
- due to common usage of a tuple of types with isinstance, tuples in a schema are treated as a single value.
    (i.e. the entire tuple is passed to isinstance.) If you would actually like for the decorator to check
    for a sequence of items corresponding to the types given, please use a list.
    If you do use a list, it will allow the actual value to be a tuple.

- The code currently checks only for isinstance(schema_type, list) for a list of types/schemas to check.
    Other Iterable type objects will be ignored unless they return true for isinstance(instance, list).

- The code for checking a schema list _is_ dependent on order.  The order of the arguments must match the order declared
    in the schema.  This seems generally desirable to me at the moment, but note that there is no alternative."""


import functools
from collections import Iterable
import sys
from copy import copy

#--------------------------
# Types
#--------------------------

class SchemaOr(object):
    """A class that allows you to allow a value as long as any of the given schemas are valid.
    Logic handling this class specifically is in _assert_format_matches."""
    def __init__(self, *annotations):
        self.schemas = annotations


#--------------------------
# Main checking functions
#--------------------------


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
        custom_raise = functools.partial(_assert_or_raise, f, arg, name)
        _assert_format_matches(ann_schema, arg, custom_raise)


def _assert_format_matches(form, data, assert_raise, key_path=None):
    """Checks that for each key value pair in form,
    there is a matching one in data where the value is the type
    specified in form."""
    if key_path is None:
        key_path = []
    is_dict = True

    try:
        form_items = form.items()
        assert_raise(isinstance(data, dict), key_path, data, dict)
    except AttributeError: # non-dictionary cases
        if isinstance(form, SchemaOr):
            reasons = []
            for i, sch in enumerate(form.schemas):
                or_key_path = copy(key_path)
                or_key_path.append(i)
                try:
                    _assert_format_matches(sch, data, assert_raise, or_key_path)
                except SchemaError as schema_err:
                    reasons.append(schema_err.args[0])
                if len(reasons) != i + 1:
                    break

            if len(reasons) == len(form.schemas):
                message = "  SchemaOr failed to validate for any schema, with these reasons:\n  "
                message = message + "\n  ".join(reasons)
                # Just want it to throw the error with function/arg name info, so we pass False
                assert_raise(False, key_path, data, form, message=message)
            return

        elif not isinstance(form, Iterable) or isinstance(form, str):
            assert_raise(isinstance(data, form), key_path, data, form)
            return

        else:
            assert_raise(isinstance(data, Iterable), key_path, data, form)
            if len(form) == 1:
                for ind, item in enumerate(data):
                    ind_key_path = copy(key_path)
                    ind_key_path.append(ind)
                    _assert_format_matches(form[0], item, assert_raise, ind_key_path)
                return
            else:
                form_items = form
                is_dict = False
    except TypeError:
        # This is raised from form.items() when form is explicity the class 'dict', in which case this is all we can check.
        assert_raise(isinstance(data, dict), key_path, data, dict)
        return

    if is_dict:
        _check_values_dict(form_items, data, assert_raise, key_path)
    else:
        _check_values_list(form_items, data, assert_raise, key_path)

    return data


def _check_values_dict(form_items, data, assert_raise, key_path):
    """Comparison logic for dictionary schemas.
    Checks the key exists in the data,
    Recurses on dicts and lists,
    and otherwise just checks the value to the form_item's value via isinstance.

    Also checks to be sure that all keys in the data source exist in form_items."""
    for key, value in form_items:

        if key not in data:
            if isinstance(value, SchemaOr):
                _call_assert_raise_no_key(assert_raise, type(None) in value.schemas, key, key_path, data, value)
            else:
                try:
                    _call_assert_raise_no_key(assert_raise, isinstance(None, value), key, key_path, data, value)
                except TypeError:
                    _call_assert_raise_no_key(assert_raise, isinstance(None, type(value)), key, key_path, data, value)

        elif isinstance(value, SchemaOr):
            key_path.append(key)
            _assert_format_matches(value, data[key], assert_raise, key_path)

        elif isinstance(value, dict):
            key_path.append(key)
            assert_raise(isinstance(data[key], dict), key_path, data[key], dict)
            _assert_format_matches(value, data[key], assert_raise, key_path)

        elif isinstance(value, (list, tuple)):
            key_path.append(key)
            assert_raise(isinstance(data[key], (list, tuple)), key_path, data[key], (list, tuple))
            # If one item is in the list, assume its homogenous and any length is okay.
            if len(data[key]) == 1:
                for i, item in enumerate(data[key]):
                    ind_key_path = copy(key_path)
                    ind_key_path.append(i)
                    _assert_format_matches(value[0], item, assert_raise, ind_key_path)
            else:
                _assert_format_matches(value, data[key], assert_raise, key_path)

        else:
            item_key_path = copy(key_path)
            item_key_path.append(key)
            assert_raise(isinstance(data[key], value), item_key_path, data[key], value)

    for key in data.keys():
        form_keys = [items[0] for items in form_items]
        assert_raise(key in form_keys,
                     key_path,
                     data,
                     form_items,
                     message="did not expect key {} in ".format(key) + "{name}" + " with value {}".format(data[key])
                     + "; key was not specified in schema.")


def _check_values_list(form_items, data, assert_raise, key_path):
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
    # data having no len() is fine as long as schema has no len()
    try:
        form_len = len(form_items)
    except TypeError:
        form_len = None
    try:
        data_len = len(data)
    except TypeError:
        data_len = None

    assert_raise(form_len == data_len,
                 key_path,
                 data,
                 form_items,
                 message=("expected a heterogenous list of length {} at ".format(form_len) +
                          "{name}" + "{},\n\tbut found length {} instead.".format(_render_key_path(key_path), data_len)))

    for index, value in enumerate(form_items):

        if isinstance(value, dict):
            key_path.append(index)
            assert_raise(isinstance(data[index], dict), key_path, data[index], dict)
            _assert_format_matches(value, data[index], assert_raise, key_path)

        elif isinstance(value, SchemaOr):
            key_path.append(index)
            _assert_format_matches(value, data[index], assert_raise, key_path)

        elif isinstance(value, list):
            key_path.append(index)
            assert_raise(isinstance(data[index], (list, tuple)), key_path, data[index], (list, tuple))
            if len(data[index]) == 1:
                key_path.append(index)
                for i, item in enumerate(data[index]):
                    ind_key_path = copy(key_path)
                    ind_key_path.append(i)
                    _assert_format_matches(value[0], item, assert_raise, ind_key_path)
            else:
                _assert_format_matches(value, data[index], assert_raise, key_path)
        else:
            item_key_path = copy(key_path)
            item_key_path.append(index)
            assert_raise(isinstance(data[index], value), item_key_path, data[index], value)


#---------------------------
# Error handling/formatting functions
#---------------------------


def _call_assert_raise_no_key(assert_raise, cond, key, key_path, value, expected):
    """Call assert_raise with an approparite message for a missing key."""
    assert_raise(cond,
                 key_path,
                 value,
                 expected,
                 message=("expected key '{}' to exist and have value of type {} at ".format(key, expected) +
                          "{name}" + "{},\n\tbut didn't find it.".format(_render_key_path(key_path))))


def _assert_or_raise(function, arg, name, cond, key_path, value, expected, message=None):
    """The 'I wish I had macros' function.  Just asserts that the conditions are true
    and raises relevant info if not."""
    if not cond:
        if message is None:
            schema_error = SchemaError(function, arg, name, key_path, value, expected)
        else:
            try:
                message = message.format(function=function, arg=arg, name=name)
            except KeyError:
                pass
            except IndexError:
                pass
            complete_message = "\n    In {}, in schema for arg '{}':\n\t".format(function, name) + message
            schema_error = SchemaError(function, arg, name, key_path, value, expected, message=complete_message)
        raise schema_error from None


class SchemaError(Exception):
    """Class used for breaking out of schema verification with info on why."""
    def __init__(self, function, arg, name, key_path, real, expected, *args, **kwargs):
        super().__init__(self, *args)
        self.function = function
        self.arg = arg
        self.name = name
        self.key_path = key_path
        self.real_value = real
        self.expected_value = expected
        if "message" in kwargs:
            self.args = (kwargs["message"],)
        else:
            self.set_expected_type_message()

    def set_expected_type_message(self):
        """Set the standard message for type mismatch."""
        key_path_trace = _render_key_path(self.key_path)
        message_base = ("\n    In {function}, in schema for arg '{name}':\n\t" +
                        "at {name}{key_path_trace}, expected value of type {expected},\n\t" +
                        "but got value '{real}' with type {real_type} instead.")
        message = message_base.format(function=self.function,
                                      name=self.name,
                                      key_path_trace=key_path_trace,
                                      expected=self.expected_value,
                                      real=self.real_value,
                                      real_type=type(self.real_value))
        self.args = (message,)


def _render_key_path(key_path):
    """Given a key path, render it in a '[0]["all"][0]["keys"]'-like format."""
    def key_format(key):
        if isinstance(key, str):
            return "['{}']".format(key)
        else:
            return "[{}]".format(key)

    key_path_strs = [key_format(key) for key in key_path]
    key_path_trace = functools.reduce(lambda x, y: x + y, key_path_strs, "")
    return key_path_trace
