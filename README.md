PY-TYPES (PYPES?!)
-------------

Gradual typing for Python 3. Python 2 won't be supported due to lack of annotations in functions.


How to use
-----------

At the moment, only runtime schemas and type-checking is supported.  These definitely have a performance overhead:
 I haven't profiled anything to check how much of an overhead there is though.

####schemas

Schema checking is meant to enforce structure and type in list and dictionary arguments.

To use schema checking, declare a structure with the types you want to see reflected in the input you get,
and then wrap the function you want to check with `@schema`, and the schema you want for a particular argumnet as the annotation.

schema assert examples (with built-in types):

```python
 test_schema = {
     "hello": int,
     "world": {
         "people": [str],
         "version": int
     },
     "optional": (int, NoneType)
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


####typechecking

Type checking is meant to flat-out test values via isinstance.  Schemas use the same thing internally,
and type checking can be mixed and matched with schemas in the same function signature. (No tests for this yet!  But will be added soon.)

Because the arguments are passed straight through to isinstance, a tuple of types can be given, and it will return true
if the argument is any one of the given types.

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

They do provide extensible "types" via the `type_defs.base.TypeFamily` metaclass, and provide some interesting
data types such as `type_defs.structured_types.TypedSequence`.  
If you do extend types using TypeFamily, the class will automatically return true for isinstance calls when compared
with any member of `my_class.type_members` (declared at top level).  If you need custom behaviour that works with
the type and schema checks, make sure that any custom logic is in the class's `__instancecheck__`.

Note that in any type-checking or schema code, "union" types can be given with a tuple, which will match
any of the types (because the type checking is done via isinstance).  So, the following code will typecheck successfully
with either an int or None instance.

```python
@typecheck
def retry_if_failed(code: (int, None)) -> None:
    # must handle None or int
    pass
```

Future enhancements
----------------

Next up on the to-do list for this project:
- add an installation package to pypi.
- static type checking! A tool to run and check what it can statically, and leave in run-time checks for what it can't.
