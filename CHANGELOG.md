# Change log

Trying to follow [semantic versioning](http://semver.org) as much as possible.

## [Unreleased][unreleased]

### Added

- Added error messaging for schema. It will now give the function and argument name, path to the part of the schema it was looking at
    (e.g. 'data[0]["key1"]'), and the expected and actual type.

### Changed

- Improved error messaging for typecheck; it now specifies what the expected and actual values were.
- Changed the directory structure for easier importing.  The previous release forced the user to use the path `py_types.py_types`.
- Fixed a bug that did not allow typecheck and schema decorators to be used together on the same function.
  - I thought this was tested before, but it appears it wasn't.

- `type_defs.composition` has been removed. [DEPRECATED]
- `runtime.asserts`'s validation functions have been removed (validate, ValidationResult, ValidationError). [DEPRECATED]
    I felt this was an inferior version of functionality already given through `type_defs.base.ValidatedType`.
    If you wish to use functions you'd want to run through validate, please use a ValidatedType with `runtime.asserts.typecheck` instead.


## 0.0.1a - 2015-07-10
Any items with the [UNUSED] tag are not normally run as part of the intended api, and are probably undocumented.

### Added
- A type definitions module, containing code with new sane types and structure for them
  - Base type classes TypeFamily and ValidatedType (`type_defs.base`).
    - These inherit attributes and use the inherited attributes in their `__instancecheck__`
  - a custom Function type to check against arity and return type in type_defs.functions. [UNTESTED]
  - Some common types that might be applicable children of TypeFamily in `type_defs.common`.
  - Typed sequence and dictionary types in `type_defs.structured_types`.
  - Some old composition operators in `type_defs.composition`. DO NOT USE. [UNUSED]
    - These will be removed in the next version.

- A runtime module containing code for ensuring correctness during a program's runtime, which includes:
  - A typecheck decorator, which asserts that arguments matched their annotated type via isinstance().
  - A validator decorator, which asserts that functions declared as annotations return true for their arguments.
  - A schema decorator, which asserts that the argument matches the detailed structure of the annotation.

- Tests module, with basic tests for all runtime code and most type-def code.

- ideal.py, a short file describing syntax possibilities for full type checking [UNUSED]
- a utils module with some unused functional operations [UNUSED]
- a static module, which contains early, experimental and untested static parsing code. [UNUSED]

### Changed
- Heavily expanded README.md to include documentation and direction.


[unreleased]: https://github.com/zekna/py-types/compare/v0.0.1a...HEAD
