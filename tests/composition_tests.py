import unittest
from asserts.asserts import (
    typecheck,
    validate,
    ValidationError,
    ValidationResult,
)
from composition import (
    JointType,
    IntersectionType,
    JointValidation,
)
from collections import (
    Iterable,
    Callable,
)


#----------------------
# Test fodder
#----------------------

# validators

@typecheck
def custom_validator(a: int) -> ValidationResult:
    if a < 5:
        return ValidationResult(True, None)
    else:
        return ValidationResult(False, "value was larger than 5.")


@typecheck
def custom_validator_two(a: int) -> ValidationResult:
    if a > 10:
        return ValidationResult(True, None)
    else:
        return ValidationResult(False, "value was smaller than 10")


range_validator = JointValidation(custom_validator,
                                  custom_validator_two)


@validate
def joint_validated(a: range_validator) -> range_validator:
    return a + 5

# types

str_or_int = JointType(str, int)


@typecheck
def type_checked(best: int, slot: str) -> str_or_int:
    if best < 10:
        return slot * best
    else:
        return best // 20


@typecheck
def type_checked_bad_return(best: int) -> str_or_int:
    if best > 10:
        return None
    else:
        return 2.54023


@typecheck
def reverse_string(s: str) -> str:
    return ''.join(reversed(s))

class Palindrome(object):
    def __init__(self, value):
        if isinstance(value, Iterable):
            if not value == reverse_string(value):
                raise TypeError("value {} is not a valid palindrome".format(value))
        else:
            if not str(value) == reverse_string(str(value)):
                raise TypeError("value {} is not a valid palindrome".format(value))

        self.value = value

    def __repr__(self):
        return self.value

    def __str__(self):
        return str(self.value)

str_palindrome = IntersectionType(Palindrome, str)

# note that this is a break of abstraction that I plan to fix
# (this should be called with @typecheck, not @validate)
@validate
def print_palindrome(pal: str_palindrome) -> None:
    print("{} say it backwards {}".format(pal, reverse_string(pal)))


# Other examples

# dependent types maybe? not sure this really counts as dependent as-is

# hacky as shit classes whoo @.@
class VectorLength_X(list):
    def __init__(self, length):
        self.length = length

    def __call__(self, value):
        result = (self.length == len(value))
        if result:
            reason = None
        else:
            reason = "value was not of length {}".format(self.length)
        return result, reason

        

@typecheck
def add_lists_len_x(length: int) -> Callable:

    @validate
    def add_lists(first: VectorLength_X(length), second: VectorLength_X(length)) -> VectorLength_X(length):
        summed_list = [x + second[i] for i, x in enumerate(first)]
        return summed_list

    return add_lists

#-------------------------
# Tests
#-------------------------

class CompositionTestCase(unittest.TestCase):
    def test_joint_validation_passes(self):
        joint_validated(-1)
        joint_validated(11)

    def test_joint_validation_fails(self):
        self.assertRaises(ValidationError, joint_validated, 1)
        self.assertRaises(ValidationError, joint_validated, 4)
        self.assertRaises(ValidationError, joint_validated, 7)
        self.assertRaises(TypeError, joint_validated, "str")
        self.assertRaises(TypeError, joint_validated, None)

    def test_joint_types_pass(self):
        type_checked(5, "a")
        type_checked(12, "b")

    def test_joint_types_fail(self):
        self.assertRaises(TypeError, type_checked_bad_return, 1)
        self.assertRaises(TypeError, type_checked_bad_return, "a")
        self.assertRaises(TypeError, type_checked_bad_return, 12)
        self.assertRaises(TypeError, type_checked_bad_return, None)

    def test_intersection_types_pass(self):
        print_palindrome("tacocat")
        print_palindrome("bob")

    def test_intersection_types_fail(self):
        self.assertRaises(TypeError, print_palindrome, "taco")
        self.assertRaises(TypeError, print_palindrome, 121)
        self.assertRaises(TypeError, print_palindrome, [1, 2, 1])

    def test_other_dependent_passes(self):
        # optimally, this setup is built into the type?
        add_lists_3 = add_lists_len_x(3)
        add_lists_1 = add_lists_len_x(1)
        self.assertEqual(add_lists_3([1, 2, 3], [3, 2, 1]), [4, 4, 4])
        self.assertEqual(add_lists_1([2], [3]), [5])

    def test_other_dependent_fails(self):
        add_lists_3 = add_lists_len_x(3)
        self.assertRaises(ValidationError, add_lists_3, [1, 2, 3], [4, 5])


if __name__ == "__main__":
    unittest.main()
