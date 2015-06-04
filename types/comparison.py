""" Module that compares different custom types in a sane way.
The main way this is done is that it's assumed that typeclasses will have a public method called
compare_to, which will be called in similar manner to isinstance.

When no such method exists, it degrades to using isinstance."""

def compare(value, intended_type):
    """Calls either compare_to or isinstance on the given values."""
    if intended_type.compare_to:
        return intended_type.compare_to(value, intended_type)
    else:
        return isinstance(value, intended_type)
