from argparse import ArgumentParser

from src.impl.degrade import degrade_video

from src.decl.encoding_options import register_encoding_options
from src.decl.filters import register_filters

import src.state.store as store
from src.state.store import runtime_value, override_runtime_value, is_enabled_at_runtime

from src.utils.name_utils import is_gif, force_gif, add_suffix
from src.utils.preset_utils import preset_file_to_args

# As much as I hate, we have to use this bait-and-switch hack again.
# This is because trying to parse_known_args() the input path,
# to use as a default for the output,
# leads us to a Catch-22.
# Either :
# A. the -h option prematurely exits when invoked, not displaying all args,
# or B. we create an add_help=False parser...but it's a runtime error with -h,
# Since input wasn't provided, and positionals are required.

DEFAULT_OUTPUT = None

def get_preset_arg_string():
    preset_parser = ArgumentParser(add_help = False)
    preset_parser.add_argument("--preset", "-pre", nargs = "?")

    known_args, other_args = preset_parser.parse_known_args()

    preset_file_path = known_args.preset

    return preset_file_to_args(preset_file_path)

def main():

    parser = ArgumentParser()

    parser.add_argument("input")
    parser.add_argument("--output", "-o", nargs = "?", default = DEFAULT_OUTPUT)

    # TODO : this pisses me off, but we have to add --preset to the main parser.
    # Otherwise, it will throw an error on parsing the global argstring!
    # The only other way would be to remove any instances of --preset
    # and its accompanying values from sys.argv...
    # ...or use "parse_known_args" for the main parse step,
    # and lose out on unrecognized arg errors entirely.
    # Basically, all available options are bad.
    parser.add_argument("--preset", "-pre", nargs = "?")

    register_encoding_options(parser)
    register_filters(parser)

    store.init_state()

    # Parse the preset file first.
    # If a preset hasn't been provided, this parses [""], which has no effect.
    parser.parse_args(get_preset_arg_string(), namespace = store.global_namespace)

    # Parse the actual args, which will, when read, override the preset.
    parser.parse_args(namespace = store.global_namespace)

    if runtime_value("output") is None:
        override_runtime_value("output", add_suffix(runtime_value("input"), "degraded"))

    if is_enabled_at_runtime("force_gif") or is_gif(runtime_value("output")):
        override_runtime_value("output", force_gif(runtime_value("output")))

    degrade_video()

if __name__ == '__main__':
    main()
