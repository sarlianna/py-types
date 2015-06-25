import unittest
from runtime.asserts import (
    typecheck,
    validate,
    ValidationError,
    ValidationResult,
)
from type_defs.composition import (
    or_comp,
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


# types

str_or_int = or_comp(str, int)

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
