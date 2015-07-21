import functools

def concat(li: "list of strings") -> str:
    return functools.reduce(lambda a, b: a + b, li)

def compose(*functions):
    def compose2(f, g):
        return lambda x: f(g(x))
    return functools.reduce(compose2, functions)

def thread_compose(*functions):
    return compose(*list(reversed(functions)))

def compose_and_call(initial_arg, *functions):
    """Given an initial value and a list of functions,
    compose the list of functions and
    call the composed function on the initial value."""
    workflow = thread_compose(*functions)
    return workflow(initial_arg)
