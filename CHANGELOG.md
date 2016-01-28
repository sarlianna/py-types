# Change log

Trying to follow [semantic versioning](http://semver.org) as much as possible.

## [Unreleased][unreleased]

### Added

### Changed

- Fixed a bug with Function raising errors on children of TypeFamily as non-valid types, breaking all custom types used with Function.
  (This fix is included in the v0.1.0a wheel.)

## [v0.1.0a] - 2016-01-27

### Added

- Added full test coverage via nose2 and fully functional tests for all code.
- Added error messaging for schema. It will now give the function and argument name, path to the part of the schema it was looking at
    (e.g. 'data[0]["key1"]'), and the expected and actual type.
    - Note that in some cases the path has been inaccurate -- bug has not been fixed in this release.
- TypeFamily, ValidatedType, and Function now raise errors if the types, validators, or return type given aren't usable.
  (Usable means either: can be pased as the second argument to isinstance (types, return types) or can be called (validators).)
- Added `profiling_info.md`, information about possible slowdown from using this in a production web api.
- Added LICENSE containing an MIT License.

### Changed

- Fixed error with SchemaOr nesting in schema checks; SchemaOr can now be used at any level of a schema without error.
- Fixed various errors with schema checking and Function
- Improved error messaging for typecheck; it now specifies what the expected and actual values were.
- Changed the directory structure for easier importing.  The previous release forced the user to use the path `py_types.py_types`.
- Fixed a bug that did not allow typecheck and schema decorators to be used together on the same function.
  - I thought this was tested before, but it appears it wasn't.

- `type_defs.composition` has been removed. [DEPRECATED]
- `runtime.asserts`'s validation functions have been removed (validate, ValidationResult, ValidationError). [DEPRECATED]
    I felt this was an inferior version of functionality already given through `type_defs.base.ValidatedType`.
    If you wish to use functions you'd want to run through validate, please use a ValidatedType with `runtime.asserts.typecheck` instead.


## [v0.0.1a] - 2015-07-10
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


[unreleased]: https://github.com/zekna/py-types/compare/v0.1.0a...HEAD
[v0.1.0a]: https://github.com/zekna/py-types/releases/tag/v0.1.0a
[v0.0.1a]: https://github.com/zekna/py-types/releases/tag/v0.0.1a
