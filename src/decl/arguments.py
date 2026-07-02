from src.types.ParserArgument import ParserArgument

DEFAULT_CRF = 64
DEFAULT_NOISE_STRENGTH = 0

DEFAULT_AUDIO_BITRATE = 5
DEFAULT_VOLUME_MULTIPLIER = 1

DEFAULT_SCALE_FACTOR = 4
DEFAULT_PASSES = 1

DEFAULT_GIF_PALETTE_SIZE = 32

business_arguments = [

    # TODO : I think staying at the low CRF is fine, we might not need randomizing

    ParserArgument(
        name = "crf",
        special_shorthand = "crf",
        default = DEFAULT_CRF
    ),

    # TODO : randomize noise strength on each pass

    ParserArgument(
        name = "noise_strength",
        special_shorthand = "e", # E. E. E. EE..E.E.EEEE..
        default = DEFAULT_NOISE_STRENGTH
    ),

    # TODO : also add gblur, randomizable

    # TODO : same as CRF for bitrate, probably fine, especially given volume concerns

    ParserArgument(
        name = "audio_bitrate",
        special_shorthand = "ba",
        type = float,
        default = DEFAULT_AUDIO_BITRATE
    ),

    # Low bitrates can lead to HEAVY clipping.
    # Users should lower the volume if they care for their ears !

    ParserArgument(
        name = "volume",
        type = float,
        default = DEFAULT_VOLUME_MULTIPLIER
    ),

    # TODO : add ability to randomize the scale factor on each pass
    # (and adjust the to-be rescale factor(s) to match)

    ParserArgument(
        name = "scale_factor",
        type = float,
        default = DEFAULT_SCALE_FACTOR
    ),

    ParserArgument(
        name = "rescale",
        type = bool,
        default = False
    ),

    # TODO : add a rescale factor ; only partially rescale
    # TODO : actually, maybe one for w and h separately...

    ParserArgument(
        name = "passes",
        special_shorthand = "n",
        default = DEFAULT_PASSES
    ),

    ParserArgument(
        name = "force_gif",
        special_shorthand = "g",
        type = bool,
        default = False,
        pass_to_compute = False
    ),

    ParserArgument(
        name = "gif_palette_size",
        special_shorthand = "p",
        default = DEFAULT_GIF_PALETTE_SIZE
    )
]

# We're just passing the args this time. No need to globalize the namespace.

def passed_business_arguments(args):
    return [
        args[argument.name] for argument in business_arguments if argument.pass_to_compute
    ]

def register_business_arguments(parser):
    for argument in business_arguments:
        argument.add_to_parser(parser)
