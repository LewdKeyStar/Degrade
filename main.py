from argparse import ArgumentParser

from src.impl.degrade import degrade_video

from src.decl.encoding_options import register_encoding_options
from src.decl.filters import register_filters

import src.state.store as store
from src.state.store import runtime_value, override_runtime_value, is_enabled_at_runtime

from src.utils.name_utils import is_gif, force_gif, add_suffix

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

    register_encoding_options(parser)
    register_filters(parser)

    store.init_state()
    parser.parse_args(namespace = store.global_namespace)

    if runtime_value("output") is None:
        override_runtime_value("output", add_suffix(runtime_value("input"), "degraded"))

    if is_enabled_at_runtime("force_gif") or is_gif(runtime_value("output")):
        override_runtime_value("output", force_gif(runtime_value("output")))

    degrade_video()

if __name__ == '__main__':
    main()
