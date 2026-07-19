from src.decl.types.ParserArgument import ParserArgument

# These options mostly have to do with process output.
# For shorthand clarity, they are all prefixed "mx"
# They're useful for the bot wrapper.

meta_options = [
    ParserArgument(
        name = "print_commands",
        special_shorthand = "mxpc",
        type = bool,
        default = False
    )
]

def register_meta_options(parser):
    for option in meta_options:
        option.add_to_parser(parser)
