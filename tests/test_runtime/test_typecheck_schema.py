from py_types.runtime import (
    typecheck,
)
from py_types.runtime.schema import (
    schema,
    SchemaOr,
    SchemaError
)

import unittest
from copy import deepcopy


#----------------------
# Test fodder
#----------------------

# asserts.py

@typecheck
def type_checked(best: int, slot: str) -> str:
    return slot * best


@typecheck
def type_checked_bad_return(a: int) -> int:
    return str(a)


@typecheck
def no_return_type() -> None:
    pass

# schema.py

NoneType = type(None)

test_schema = {
    "hello": int,
    "world": {
        "people": [str],
        "version": int
    },
    "optional": SchemaOr(int, NoneType)
}

@schema
def schema_checked(a: test_schema) -> test_schema:
    b = deepcopy(a)
    b["hello"] += 5
    if b["world"]["people"]:
        b["world"]["people"][0] = "Bob"
    b["world"]["version"] += 1
    return b


#----------------------
# Tests
#----------------------

class TypecheckTestCase(unittest.TestCase):
    """Tests for py_types.runtime.typecheck"""
    def test_check_pass(self):
        type_checked(2, "wut ")

    def test_check_args_fail(self):
        self.assertRaises(TypeError, type_checked, "5", "wut ")
        self.assertRaises(TypeError, type_checked, 5, 20)

    def test_check_result_fails(self):
        self.assertRaises(TypeError, type_checked_bad_return, 2)

    def test_check_no_return(self):
        """Test that when None is specified as a return, returning a value throws an error."""
        @typecheck
        def no_return_type() -> None:
            pass
        @typecheck
        def no_return_type_wrong() -> None:
            return True
        self.assertRaises(TypeError, no_return_type_wrong)
        no_return_type()

    def test_values_fall_through(self):
        """Test that values passed to typecheck are ignored by typecheck."""
        @typecheck
        def takes_ints(a: 5, b: {"a": 20}) -> 11:
            return "hello"

        # None of these should throw an error
        takes_ints(7, 12)
        takes_ints("h", "b")
        takes_ints({"hello": "there"}, ["bob"])


class SchemaTestCase(unittest.TestCase):
    """Tests for py_types.runtime.schema"""
    def test_schema_passes(self):
        """Test correct schemas get through."""
        test = {"hello": 5, "world": {"people": ["Alice"], "version": 1}}
        with_optional = {"hello": 2, "world": {"people": ["Jack", "Jill"], "version": 0}, "optional": 20}
        empty_people = {"hello": 4, "world": {"people": [], "version": 2}}

        schema_checked(test)
        schema_checked(with_optional)
        schema_checked(empty_people)

    def test_invalid_schema_throws(self):
        tests = []
        tests.append({"hello": "what?!"})
        tests.append({"helloo": 5})
        tests.append([("hey", "you")])
        tests.append(2)
        tests.append({"hello": 5, "world": {"people": "gone now"}})

        for test in tests:
            self.assertRaises(SchemaError, schema_checked, test)

    def test_nested_dicts(self):
        @schema
        def test_function(arg: {"a": {"b": {"c": int}}}):
            pass

        test_function({"a": {"b": {"c": 5}}})
        self.assertRaises(SchemaError, test_function, {"a": {"b": ["c", 5]}})

    def test_simple_types(self):
        """Test that schema will simply typecheck simple types."""
        @schema
        def test_function(arg: int) -> str:
            return str(arg)

        test_function(5)
        self.assertRaises(SchemaError, test_function, "5")

    def test_nested_lists(self):
        @schema
        def test_function(arg: [[str], [int]]):
            pass

        test_function([["a", "b"], [5, 6]])
        test_function([["a"], [5]])
        self.assertRaises(SchemaError, test_function, [[5, 6], ["a", "b"]])
        self.assertRaises(SchemaError, test_function, [[5, 6]])
        self.assertRaises(SchemaError, test_function, [["a", "b"]])

    def test_nested_str(self):
        """Test that a string in a schema isn't treated as an iterable."""
        @schema
        def test_function(arg: {"a": str}):
            pass

        test_function({"a": "hello there"})

    def test_schemaor(self):
        """Test that a top-level schemaor accepts either of its arguments"""
        test_schema = SchemaOr({"count": int}, float)

        @schema
        def test_function(count_struct: test_schema) -> test_schema:
            return {"count": 5}

        test_function({"count": 5})
        test_function(5.)
        self.assertRaises(SchemaError, test_function, {})
        self.assertRaises(SchemaError, test_function, ["hello", 2])

    def test_schemaor_homogenous_lists(self):
        @schema
        def test_function_hol(count_struct: SchemaOr([str], [int])) -> int:
            return 5
        test_function_hol(["a", "b", "c"])
        test_function_hol(["a"])
        test_function_hol([2])
        test_function_hol([1, 2, 3, 6])
        self.assertRaises(SchemaError, test_function_hol, None)
        self.assertRaises(SchemaError, test_function_hol, [{"hey": "you"}])

    def test_schemaor_heterogenous_lists(self):
        @schema
        def test_function_hel(count_struct: SchemaOr([str, int, str], [int, str])) -> int:
            return 5
        test_function_hel(["a", 5, "c"])
        test_function_hel([2, "a"])
        self.assertRaises(SchemaError, test_function_hel, None)
        self.assertRaises(SchemaError, test_function_hel, [{"hey": "you"}])
        self.assertRaises(SchemaError, test_function_hel, ["a", 5, "c", 6])
        self.assertRaises(SchemaError, test_function_hel, ["a", 5, 6])
        self.assertRaises(SchemaError, test_function_hel, ["a", 5])

    def test_schemaor_dicts(self):
        @schema
        def test_function_d(count_struct: SchemaOr({"a": int, "b": str}, {"c": str})) -> int:
            return 5
        test_function_d({"a": 4, "b": "4"})
        test_function_d({"c": "nope"})
        self.assertRaises(SchemaError, test_function_d, {"a": "wrong", "b": "right"})
        self.assertRaises(SchemaError, test_function_d, {"c": 5})
        self.assertRaises(SchemaError, test_function_d, 5)
        self.assertRaises(SchemaError, test_function_d, "hey")
        self.assertRaises(SchemaError, test_function_d, {})
        self.assertRaises(SchemaError, test_function_d, {"d": 5, "e": "s"})

    def test_schemaor_nested_dict(self):
        """Test that SchemaOr objects work from inside dictionaries and lists."""
        test_schema = {"count": SchemaOr(int, type(None))}

        @schema
        def test_function(count_struct: test_schema) -> test_schema:
            return {"count": 5}

        test_function({"count": 5})
        test_function({"count": None})
        test_function({})
        self.assertRaises(SchemaError, test_function, "hello")
        self.assertRaises(SchemaError, test_function, {"count": "hello"})
        self.assertRaises(SchemaError, test_function, {"count": {}})
        self.assertRaises(SchemaError, test_function, {"hello": 5})
        self.assertRaises(SchemaError, test_function, ["hello"])

    def test_schemaor_nested_homogenous_lists(self):
        @schema
        def test_function_hol(count_struct: [SchemaOr(str, int)]):
            pass
        test_function_hol(["a", "b", "c"])
        test_function_hol(["a"])
        test_function_hol([2])
        test_function_hol([1, "a", 3, "b"])
        self.assertRaises(SchemaError, test_function_hol, None)
        self.assertRaises(SchemaError, test_function_hol, [{"hey": "you"}])

    def test_schemaor_nested_heterogenous_lists(self):
        @schema
        def test_function_hel(count_struct: [SchemaOr(str), SchemaOr(int)]):
            pass
        test_function_hel(["a", 5])
        self.assertRaises(SchemaError, test_function_hel, [2, "a"])
        self.assertRaises(SchemaError, test_function_hel, None)
        self.assertRaises(SchemaError, test_function_hel, [{"hey": "you"}])
        self.assertRaises(SchemaError, test_function_hel, ["a", 5, "c", 6])
        self.assertRaises(SchemaError, test_function_hel, ["a", 5, 6])

    def test_schemaor_nested_dict_in_dict(self):
        """Test that a SchemaOr containing a dict inside of a dict functions as expected."""
        @schema
        def test_function_nd(count_struct: {"test": SchemaOr({"different_test": int}, type(None))}):
            pass

        test_function_nd({"test": {"different_test": 5}})
        test_function_nd({"test": None})
        test_function_nd({})
        self.assertRaises(SchemaError, test_function_nd, {"test": {"different_test": {"other_test": 5}}})
        self.assertRaises(SchemaError, test_function_nd, {"wrong_key": {"different_test": 5}})
        self.assertRaises(SchemaError, test_function_nd, {"test": {"different_test": 5}, "extra_key": 7})
        self.assertRaises(SchemaError, test_function_nd, [2, "a"])
        self.assertRaises(SchemaError, test_function_nd, None)

    def test_nested_tuples(self):
        """Test that tuples in schemas are treated as iterables/lists and not as sum types/values
        (basically, test that they don't get passed to isinstance)
        """
        @schema
        def test_function_nt(count_struct: {"test": (int, str)}):
            pass

        test_function_nt({"test": (5, "left")})
        test_function_nt({"test": [3, "right"]})
        self.assertRaises(SchemaError, test_function_nt, {"test": 5})
        self.assertRaises(SchemaError, test_function_nt, {"test": "middle"})
