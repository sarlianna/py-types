#########
# This file documents the syntax I'd ideally like to have as an end result of the gradual typing.
# should be considered a temproray document, to be replaced by tests later.
#########

# composition of types should be easy
StrInt = JointType(str, int)

# possible declarative syntax for non-arguments
@typecheck([("i", int), ("temp", StrInt)])
def calculate(start: int, end: int) -> StrInt:
    # if an assignment such as temp = 2.50 were made here, the checker should error (STATIC)
    temp = 0
    for i in range(start, end):
        temp = concat(temp, i, "@")

    # temp can only be a str or int, and slice syntax can't work on ints,
    # so checker should be able to assume both temp and result are now of type str. (STATIC)
    result = temp[5:]
    return result

@typecheck
def concat(base: StrInt, num: int, char: "str") -> str:
    result = case(typeof(base), { int: str(base * num) + char,
                                  str: (base + char) * num,
                                  "default": ""})
    return result

@typecheck
def case(test_value, cases):
    result = None
    for key, val in cases:
        if key != "default" and test_value == key:
            result = val
            break

    if result is None:
        if not cases.has_key("default"):
            raise ValueError("Case statement had no default key when no other cases matched.")
        result = cases["default"]

    return result
