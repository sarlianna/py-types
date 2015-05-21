from types import ComplexType

if ComplexType:
    NUMBER_TYPECLASS_TYPES = (int, long, float, ComplexType)
else:
    NUMBER_TYPECLASS_TYPES = (int, long, float)

class Number(object):
    """ """
    @class_method
    def is_number(value):
        tests = [isinstance(value, t) for t in NUMBER_TYPECLASS_TYPES]
        return True in tests

    def __init__(self, value):
        if self.is_number(value):
            self.value = value
        else:
            def check_conversion_success(val, t):
                """Returns True if no exception was thrown, otherwise False"""
                try:
                    t(val)
                except Exception as e:
                    return False
                return True

            conversions = [check_conversion_success(value, t) for t in NUMBER_TYPECLASS_TYPES]
            count = len([conv for conv in conversions if conv])
            if count > 1:
                types_convs = zip(NUMBER_TYPECLASS_TYPES, conversions)



