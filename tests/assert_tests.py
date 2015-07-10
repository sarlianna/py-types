from py_types.runtime.asserts import (
    typecheck,
    validate,
    ValidationError,
    ValidationResult,
)
from py_types.runtime.schema import (
    schema
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
def custom_validator(a: int) -> ValidationResult:
    if a < 5:
        return ValidationResult(True, None)
    else:
        return ValidationResult(False, "value was larger than 5.")


@validate
def validated(a: custom_validator) -> custom_validator:
    return a + 5

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
    "optional": (int, NoneType)
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
    def test_check_pass(self):
        type_checked(2, "wut ")

    def test_check_args_fail(self):
        self.assertRaises(TypeError, type_checked, "5", "wut ")
        self.assertRaises(TypeError, type_checked, 5, 20)

    def test_check_result_fails(self):
        self.assertRaises(TypeError, type_checked_bad_return, 2)

    def test_check_no_return(self):
        @typecheck
        def no_return_type() -> None:
            pass
        @typecheck
        def no_return_type_wrong() -> None:
            return True
        self.assertRaises(TypeError, no_return_type_wrong)
        no_return_type()

    def test_valid_pass(self):
        validated(-1)

    def test_valid_arg_fails(self):
        self.assertRaises(ValidationError, validated, 6)

    def test_valid_result_fails(self):
        self.assertRaises(ValidationError, validated, 3)

    def test_valid_no_return(self):
        @validate
        def no_return_type() -> None:
            pass
        @validate
        def no_return_type_wrong() -> None:
            return True
        self.assertRaises(ValidationError, no_return_type_wrong)
        no_return_type()


class SchemaTestCase(unittest.TestCase):
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
            self.assertRaises(AssertionError, schema_checked, test)


if __name__ == "__main__":
    unittest.main()
