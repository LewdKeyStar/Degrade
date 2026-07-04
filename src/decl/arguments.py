from src.types.ParserArgument import ParserArgument

DEFAULT_CRF = 64 # TODO : apparently this is identical to 51, but sources are contradictory

# Scaling in a separate pass can be useful to upscale low-res H264 artifacts,
# Creating a "shapely", "blurry" look, rather than pixelated.
# However, for this, the rescale needs its own, higher CRF.

DEFAULT_SCALE_BACK_POST_ENCODE_CRF = 17

# lower values, of course, lead to higher file sizes, but also...
# to different types of artifact :
# for instance, on test videos, 17 preserves mouths but 1 doesn't!

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

    # For media degradation, downscaling is an excellent operation.

    # TODO : add ability to randomize the scale factor on each pass
    # (and adjust the to-be rescale factor(s) to match)

    ParserArgument(
        name = "scale_factor",
        type = float,
        default = DEFAULT_SCALE_FACTOR
    ),

    # There are two types of rescale when it comes to degradation :

    # 1. Pre-encode rescale, which immediately follows downscale in the same filterchain,
    # Prior to video encoding.
    # This creates noisy, visible "hyperpixels".

    ParserArgument(
        name = "scale_back_pre_encode",
        special_shorthand = "sbe",
        type = bool,
        default = False
    ),

    # 2. Isolated rescale on a previously encoded video.
    # This magnifies the artifacts of the encoded H264 frame,
    # And tends to create a "shapely", "blurry", "glossy" effect, as opposed to blocky.

    # TODO : make these two mutually exclusive !

    ParserArgument(
        name = "scale_back_post_encode",
        special_shorthand = "sbo",
        type = bool,
        default = False
    ),

    # For isolated rescale to work, it must operate at high fidelity,
    # That is, with a low CRF, contrary to the rest of the filterchain.
    # Therefore it has its own CRF parameter.

    ParserArgument(
        name = "scale_back_post_encode_crf",
        special_shorthand = "sbocrf",
        type = int,
        default = DEFAULT_SCALE_BACK_POST_ENCODE_CRF
    ),

    # Another method is to re-encode the video multiple times.
    # This tends to go too far with isolated rescale, though,
    # But synergizes well with pre-encode rescale.

    ParserArgument(
        name = "passes",
        special_shorthand = "n",
        default = DEFAULT_PASSES
    ),

    # TODO : add a "rescale factor" ; only partially rescale
    # TODO : actually, maybe one for w and h separately...

    # TODO : randomize noise strength on each pass

    ParserArgument(
        name = "noise_strength",
        special_shorthand = "e", # E. E. E. EE..E.E.EEEE..
        default = DEFAULT_NOISE_STRENGTH
    ),

    ParserArgument(
        name = "blur_sigma",
        special_shorthand = "sg",
        type = float
    ),

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
