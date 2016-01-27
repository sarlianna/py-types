import unittest
from unittest import mock
from py_types.type_defs.base import (
    TypeFamily,
    ValidatedType,
)

class TypeFamilyTestCase(unittest.TestCase):
    def set_up(self):
        pass

    def test_type_members_become_registered(self):
        """Test that arguments passed into type_members become part of
        _registered_types attribute."""
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

    def test_invalid_type_members(self):
        """Test that trying to register invalid types throws an error."""
        with self.assertRaises(TypeError):
            class InvalidType(metaclass=TypeFamily):
                type_members = [5, "typezz"]

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
        """Regression test for a bug where all classes using TypeFamily shared
        type instance registration."""
        class NewType(metaclass=TypeFamily):
            type_members = [int]

        class SecondNewType(NewType):
            type_members = [str]

        class UnrelatedType(metaclass=TypeFamily):
            type_members = [list]

        self.assertTrue(isinstance([5], UnrelatedType))
        self.assertFalse(isinstance("h", UnrelatedType))
        self.assertFalse(isinstance(5, UnrelatedType))


class ValidatedTypeTestCase(unittest.TestCase):
    def set_up(self):
        pass

    def test_type_members_and_validators_become_registered(self):
        """Test that validators allow type_members to be registered
        to _registered_types and that validators are registered to
        _registered_validators."""
        def always(instance):
            return True

        class NewType(metaclass=ValidatedType):
            type_members = [int, str]
            validators = [always]

        new_type = NewType()
        self.assertEqual(new_type._registered_types, new_type.type_members)
        self.assertTrue(int in new_type._registered_types)
        self.assertTrue(str in new_type._registered_types)
        self.assertEqual(new_type._registered_validators, new_type.validators)
        self.assertTrue(always in new_type._registered_validators)

    def test_type_members_and_validators_are_used(self):
        """Test that validators and type members specified in are run during isinstance checks."""
        def sometimes(instance):
            if instance == 2:
                return False
            return True

        class NewType(metaclass=ValidatedType):
            type_members = [int, str]
            validators = [sometimes]

        self.assertTrue(isinstance(5, NewType))
        self.assertTrue(isinstance("test", NewType))
        self.assertFalse(isinstance([2], NewType))
        self.assertFalse(isinstance(2, NewType))

    def test_invalid_type_members_validators(self):
        """Test that trying to register invalid types or validators throws an error."""
        with self.assertRaises(TypeError):
            class InvalidType(metaclass=ValidatedType):
                type_members = [5, "typezz"]
                validators = []

        with self.assertRaises(TypeError):
            class InvalidType(metaclass=ValidatedType):
                type_members = [int]
                validators = ["hello"]

    def test_type_members_and_validators_are_inherited(self):
        """Test that a class inheriting from a validated type will inherit type members and validators
        and be registered to them."""
        def always(instance):
            return True

        def sometimes(instance):
            if instance == 2:
                return False
            return True

        class NewType(metaclass=ValidatedType):
            type_members = [int]
            validators = [always]

        class SecondNewType(NewType):
            type_members = [str]
            validators = [sometimes]

        self.assertTrue(isinstance(5, SecondNewType))
        self.assertTrue(isinstance("h", SecondNewType))

        self.assertTrue(isinstance(5, NewType))
        self.assertFalse(isinstance("h", NewType))

        self.assertTrue(isinstance(2, NewType))
        self.assertFalse(isinstance(2, SecondNewType))

    def test_type_member_inheritance_applies_only_to_children(self):
        """Regression test for a bug where all classes using metaclasses shared
        type instance registration.
        Validators don't use instance registration in the same way,
        so they shouldn't be affected by this bug."""
        class NewType(metaclass=ValidatedType):
            type_members = [int]

        class SecondNewType(NewType):
            type_members = [str]

        class UnrelatedType(metaclass=ValidatedType):
            type_members = [list]

        self.assertTrue(isinstance([5], UnrelatedType))
        self.assertFalse(isinstance("h", UnrelatedType))
        self.assertFalse(isinstance(5, UnrelatedType))
