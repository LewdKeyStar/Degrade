from src.decl.types.ParserArgument import ParserArgument

DEFAULT_CRF = 64 # TODO : apparently this is identical to 51, but sources are contradictory

DEFAULT_AUDIO_BITRATE = 5

DEFAULT_PASSES = 1

encoding_options = [

    # TODO : I think staying at the low CRF is fine, we might not need randomizing

    ParserArgument(
        name = "crf",
        special_shorthand = "crf",
        default = DEFAULT_CRF
    ),

    # One of the key ways to degrade video is to re-encode it multiple times.
    # This tends to go too far with isolated rescale, though,
    # But synergizes well with pre-encode rescale.

    ParserArgument(
        name = "passes",
        special_shorthand = "n",
        default = DEFAULT_PASSES
    ),

    # TODO : same as CRF for bitrate, probably fine, especially given volume concerns

    ParserArgument(
        name = "audio_bitrate",
        special_shorthand = "ba",
        type = float,
        default = DEFAULT_AUDIO_BITRATE
    ),

    ParserArgument(
        name = "force_gif",
        special_shorthand = "g",
        type = bool,
        default = False
    )
]

def register_encoding_options(parser):
    for argument in encoding_options:
        argument.add_to_parser(parser)
