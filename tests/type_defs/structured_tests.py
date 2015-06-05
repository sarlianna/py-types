import unittest
from type_defs.base import TypeFamily
from type_defs.common import Any
from type_defs.structured_types import (
    TypedSequence,
    TypedDict,
)

class StructuredTypesTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_sequence_isinstance_only_for_homogenous_lists(self):
        """Test that a list of all appropriate type will be determined an instance,
        and nothing else."""
        IntSeq = TypedSequence(int)
        valid = [1, 2, 3, 4]
        invalid = [1, "h", 3, 4]

        self.assertTrue(isinstance(valid, IntSeq))
        self.assertFalse(isinstance(invalid, IntSeq))

    def test_custom_types_work_with_typed_sequence(self):
        """Test that a list of custom types will still work correctly."""
        class StrInt(metaclass=TypeFamily):
            type_members = [int, str]

        StrIntSequence = TypedSequence(StrInt)
        valid = ["h", 1, 2, "three", 4]
        invalid = [{"a": 1}, 2]

        self.assertTrue(isinstance(valid, StrIntSequence))
        self.assertFalse(isinstance(invalid, StrIntSequence))

    def test_dict_isinstance_only_for_homogenous_dicts(self):
        """Test that a dict of all appropriate type will be determined an instance,
        and nothing else."""
        StrIntDict = TypedDict(str, int)
        valid = {"cars": 20,
                 "vans": 5,
                 "trucks": 30}
        invalid = {"cars": "three",
                   "vans": 27}
        also_invalid = {5: 20}

        self.assertTrue(isinstance(valid, StrIntDict))
        self.assertFalse(isinstance(invalid, StrIntDict))
        self.assertFalse(isinstance(also_invalid, StrIntDict))

    def test_custom_types_work_with_typed_dict(self):
        """Test that a dict of custom types will still work correctly."""
        class StrInt(metaclass=TypeFamily):
            type_members = [int, str]

        StrIntValDict = TypedDict(Any, StrInt)

        def fn(a):
            return a
        valid = {"cars": 20,
                 5: "hey there",
                 fn: 30}
        invalid = {"cars": 27,
                   25: 20.5}
        also_invalid = {"hey": fn}

        self.assertTrue(isinstance(valid, StrIntValDict))
        self.assertFalse(isinstance(invalid, StrIntValDict))
        self.assertFalse(isinstance(also_invalid, StrIntValDict))


if __name__ == "__main__":
    unittest.main()
