import unittest
from type_defs.base import (
    TypeFamily,
)

class TypeFamilyTestCase(unittest.TestCase):
    def set_up(self):
        pass

    def test_type_members_become_registered(self):
        """Test that arguments passed into type_members become part of
        __registered_types__ attribute."""
        class NewType(metaclass=TypeFamily):
            type_members = [int, str]

        new_type = NewType()
        self.assertEqual(new_type._registered_types, new_type.type_members)
        self.assertTrue(int in new_type._registered_types)
        self.assertTrue(str in new_type._registered_types)

    def test_typeclass_register(self):
        """Test that registering to typeclass' type_members works as expected."""
        class NewType(metaclass=TypeFamily):
            type_members = [int, str]

        self.assertTrue(isinstance(5, NewType))
        self.assertTrue(isinstance("test", NewType))
        self.assertFalse(isinstance([2], NewType))

    def test_type_members_are_inherited(self):
        """Test that a class inheriting from a type family will inherit type members
        and be registered to them."""
        class NewType(metaclass=TypeFamily):
            type_members = [int]

        class SecondNewType(NewType):
            type_members = [str]

        self.assertTrue(isinstance(5, SecondNewType))
        self.assertTrue(isinstance("h", SecondNewType))

        self.assertTrue(isinstance(5, NewType))
        self.assertFalse(isinstance("h", NewType))

    def test_type_member_inheritance_applies_only_to_children(self):
        class NewType(metaclass=TypeFamily):
            type_members = [int]

        class SecondNewType(NewType):
            type_members = [str]

        class UnrelatedType(metaclass=TypeFamily):
            type_members = [list]

        self.assertTrue(isinstance([5], UnrelatedType))
        self.assertFalse(isinstance("h", UnrelatedType))
        self.assertFalse(isinstance(5, UnrelatedType))


if __name__ == "__main__":
    unittest.main()
