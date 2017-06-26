PY-TYPES (PYPES?!)
-------------

Lightweight, gradual typing for Python 3. Python 2 won't be supported due to lack of annotations in functions.


Installation
-----------

Currently there is no package on PyPI, which will change soon.

After cloning the repo, you can install with `pip install .`,
or you can build your own wheel via `python setup.py bdist_wheel`.  After running the `bdist_wheel`
command a .whl file (`py_types-<version>-py3-none-any.whl`) will be available in dist/.  
You can pip install the .whl file directly via `pip install py_types-<version>-py3-none-any.whl`.


Tests
----------------
Tests can be run via `nose2` from the root directory.

If nose2 is installed, you can also run `python3 setup.py test` to run the tests, but note that nose2 does have some limitations
when run this way (see https://nose2.readthedocs.org/en/latest/differences.html#limited-support-for-python-setup-py-test).


How to use
-----------

At the moment, only runtime schemas and type-checking is supported.  These definitely have a performance overhead;
for details about how this may affect a flask webserver, see profiling_info.md.  
It's recommended that you use this library for development/testing only, by defining the typecheck/schema functions based on your environment.
(Import them for non-production code, define them as no-ops in production code.)
I'd like to add this to the library itself, but don't have a clean way to do that at the moment.


#### schemas

Schema checking is meant to enforce structure and type in list and dictionary arguments.

To use schema checking, declare a structure with the types you want to see reflected in the input you get,
and then wrap the function you want to check with `@schema`, and the schema you want for a particular argument as the annotation.

schema examples (with built-in types):

```python
 test_schema = {
     "hello": int,
     "world": {
         "people": [str],
         "version": int
     },
     "optional": SchemaOr(int, type(None))
 }

 @schema
 def schema_checked(a: test_schema) -> test_schema:
     b = deepcopy(a)
     b["hello"] += 5
     if b["world"]["people"]:
         b["world"]["people"][0] = "Bob"
     b["world"]["version"] += 1
   return b
```

```python
from functools import reduce

list_schema = [int]

@schema
def sum(li: list_schema) -> int:
    def add(a, b):
        return a + b

    return reduce(add, li)
```

Note that custom types as well as built-ins can be used.  (See "Sane, friendlier types" for more on custom ones.)


Homogenous, heterogenous lists - Note that when using a list as a schema, the schema decorator differentiates between two types of lists.
If your schema's list value has one element, it's homogenous, and schema will assume that any length is acceptable, as long as every element
matches the schema of the one element that the list has.  If there are multiple elements, it is heterogenous.  Schema assumes that the length
of heterogenous lists must match the number of elements specified, and that each item in the list will match the schemas in the list in order.
(I.e., they are order-dependent.)  
If some of this behaviour seems undesirable, custom or validated types can be used to combat some of it, but there is currently no other solid solution.
If you have a good solution for this, please tell me or submit a PR!

#### typechecking

Type checking is meant to flat-out test values via isinstance.  Schemas use the same thing internally,
and type checking can be mixed and matched with schemas in the same function signature. (No tests for this yet!  But will be added soon.)

Because the arguments are passed straight through to isinstance, a tuple of types can be given, and it will return true
if the argument is any one of the given types.
Note that this is slightly different than schema, which interprets tuples as literal tuples, and uses SchemaOr for declaring one of any type.

some typechecking examples:
```python
# this will run normally unless best or slot are incorrect types
@typecheck
def type_checked(best: int, slot: str) -> str:
    return slot * best

# this will always throw an exception due to return type
@typecheck
def bad_return(a: int) -> int:
    return str(a)

```

This is meant to be used with custom types/classes, and is mostly just a stepping stone for better applications of type checking.


Sane, friendlier types
----------------

Since python's built-ins weren't really meant for type checking or static analysis, I'm working on
building out new types inspired by Haskell/Rust but suitable for python.

There are some working definitions and code in type_defs, but they need some serious work and don't cover
anywhere near what they should.

#### base, inheritable type classes

They do provide extensible "types" via the `type_defs.base.TypeFamily` metaclass, and provide some interesting
data types such as `type_defs.structured_types.TypedSequence`.  
If you do extend types using TypeFamily, the class will automatically return true for isinstance calls when compared
with any member of `my_class.type_members` (declared at top level).  If you need custom behaviour that works with
the type and schema checks, make sure that any custom logic is in the class's `__instancecheck__`.

`type_defs.base.ValidatedType` has been added, which essentially inherits a list of validator functions and type
values.  Its `__instancecheck__` is customized to run the validators on the given value.


#### function types

Added a custom Function type in `type_defs.functions`.  This type allows you to specify and check for callables with
specific arity (number of arguments) and return types. Added because checking against Callable was not a very good guarantee!

Note that these types purposefully do not handle schema declarations as a return type.  The Function type will
only compare the direct return type of the function given.  
If you'd like a particular function's return value to be schema checked at runtime, just define the function with the @schema
decorator.


#### notes on use of isinstance

Note that in any type-checking, "union" types can be given with a tuple, which will match
any of the types (because the type checking is done via isinstance).  So, the following code will typecheck successfully
with either an int or None instance.

```python
@typecheck
def retry_if_failed(code: (int, type(None))) -> type(None):
    # must handle None or int
    pass
```

Because everything is done through isinstance, the custom types should compose and work normally with other types, classes, etc.

Please note again that this is different from how the schema decorator works -- if you want to accept multiple
types or schemas with the schema decorator, please use the the `runtime.schema.SchemaOr` class with the types/schemas as args.


Known Bugs
----------------

- When reporting errors at a specific location in a schema, the given path is always incorrect. E.g. in the message
  `value for schema at arg_name["key_name"][0]["key"]`, arg_name["key_name"][0]["key"] is not the actual value it's looking at and
  may not even be a valid value. The larger the schema, the more likely it is to be inaccurate.


Future enhancements
----------------

Next up on the to-do list for this project:
- add an installation package to pypi.
- support for python 3.5's `typing` package
- Move some of this README to documentation instead.
- static type checking! A tool to run and check what it can statically, and leave in run-time checks for what it can't.
