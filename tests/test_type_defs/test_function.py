import unittest
from py_types.type_defs.functions import Function
from py_types.type_defs.common import Any


class FunctionTypeTestCase(unittest.TestCase):
    def set_up(self):
        pass

    def test_object_creation_sets_properties(self):
        func = Function(2, int)
        self.assertEqual(func.arity, 2)
        self.assertEqual(func.return_type, int)

    def test_arity_affects_isinstance_checks(self):
        def two_vars(variable, other_variable) -> int:
            return int(other_variable * variable)
        def function(variable) -> int:
            return int(variable)
        func = Function(2, int)
        self.assertTrue(isinstance(two_vars, func))
        self.assertFalse(isinstance(function, func))

    def test_return_type_affects_isinstance_checks(self):
        def other(variable) -> str:
            return str(variable)
        def function(variable) -> int:
            return int(variable)
        func = Function(1, str)
        self.assertTrue(isinstance(other, func))
        self.assertFalse(isinstance(function, func))

    def test_invalid_arity_throws_error(self):
        """Test that impossible arities throw errors (e.g. negative arity)"""
        self.assertRaises(ValueError, Function, -1, int)

    def test_invalid_return_type_throws_error(self):
        """Test that a return type not of type <class type> will throw an error."""
        self.assertRaises(TypeError, Function, 1, "hello")

    def test_no_return_annotation_passes(self):
        """Test that a function that has no return annotation will
        return True for an isinstance check as long as it has the correct arity."""
        def other(variable) -> str:
            return str(variable)
        def function(variable):
            return int(variable)
        func = Function(1, str)
        self.assertTrue(isinstance(other, func))
        self.assertTrue(isinstance(function, func))

    def test_type_family_children_are_valid(self):
        """Regression test where children of TypeFamily were rejected as not types."""
        def valid_function() -> Function(1, Any):
            return lambda x: x + 1

        a = valid_function()
