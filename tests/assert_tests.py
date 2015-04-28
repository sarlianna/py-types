from asserts import (
    typecheck,
    validate,
    ValidationError,
    ValidationResult,
)

import unittest


#----------------------
# Test fodder
#----------------------

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
            print("not returning anything!")
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
            print("not returning anything!")
        @validate
        def no_return_type_wrong() -> None:
            return True
        self.assertRaises(TypeError, no_return_type_wrong)
        no_return_type()

if __name__ == "__main__":
    unittest.main()
