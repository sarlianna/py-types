import ast
import inspect
import sys
import argparse

from ..runtime.asserts import typecheck
from ..types.comparison import compare


@typecheck
def pretty_print_defs(defs: list) -> None:
    for d in defs:
        print("Function definition for {}".format(d["name"]))
        print("Arguments:")
        for arg in d["args"]:
            arg_type = "untyped"
            if arg[2]:
                arg_type = arg[2].id
            print("\t{} : type {}".format(arg[1], arg_type))

        if len(d["args"]) == 0:
            print("\tNo arguments.")

        return_type = None
        if d["return"]:
            return_type = d["return"].id
        print("Return type: {}".format(return_type))
        print("")


@typecheck
def parse(filename: str) -> list:
    """Parses and does basic analysis of functions declared at the top level of a file."""
    with open(filename, "r") as file_to_parse:
        a = file_to_parse.read()
        file_ast = ast.parse(a)
        # initial pass -- get all function definitions, their names, args, and annotations
        @typecheck
        def get_name_annotations(block) -> dict:
            if not compare(block, ast.FunctionDef):
                return
            return_annotation = block.returns
            arg_annotations = []
            for i, arg in enumerate(block.args.args):
                arg_annotations.append((i, arg.arg, arg.annotation))

            fn_name = block.name
            annotations = {
                "name": fn_name,
                "return": return_annotation,
                "args": arg_annotations
            }

            return annotations

        definitions = [get_name_annotations(block) for block in file_ast.body]

        pretty_print_defs(definitions)

        # second pass -- find all expressions, double check origins of any arguments passed to any function in definitions
        def depth_first_traversal(ast_tree, filter_type, results: list) -> ast.Module:
            pass

        return definitions


if __name__ == "__main__":
    parse("static/example_parse_me.py")
