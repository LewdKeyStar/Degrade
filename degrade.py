from argparse import ArgumentParser
from src.decl.arguments import register_business_arguments, passed_business_arguments

from src.utils.name_utils import is_gif, force_gif, add_suffix
from src.impl.degrade import degrade

# As much as I hate, we have to use this bait-and-switch hack again.
# This is because trying to parse_known_args() the input path,
# to use as a default for the output,
# leads us to a Catch-22.
# Either :
# A. the -h option prematurely exits when invoked, not displaying all args,
# or B. we create an add_help=False parser...but it's a runtime error with -h,
# Since input wasn't provided, and positionals are required.

DEFAULT_OUTPUT = None

def main():

    parser = ArgumentParser()

    parser.add_argument("input")
    parser.add_argument("--output", "-o", nargs = "?", default = DEFAULT_OUTPUT)

    register_business_arguments(parser)

    args = vars(parser.parse_args())

    if args["output"] is None:
        args["output"] = add_suffix(args["input"], "degraded")

    if args["force_gif"] or is_gif(args["output"]):
        args["output"] = force_gif(args["output"])

    degrade(
        args["input"],
        args["output"],

        *passed_business_arguments(args)
    )

if __name__ == '__main__':
    main()
