from src.decl.types.Filter import Filter
from src.decl.types.ParserArgument import ParserArgument

from src.state.store import runtime_value, is_enabled_at_runtime

from src.utils.filter_utils import filter_join, h264_pad_filter
from src.utils.sort_utils import priority_sort

from src.decl.utils import is_dedicated_rescale_pass, is_not_dedicated_rescale_pass

DEFAULT_NOISE_STRENGTH = 0

DEFAULT_VOLUME_PERCENTAGE = 1

DEFAULT_SCALE_FACTOR = 4

DEFAULT_GIF_PALETTE_SIZE = 32

DEFAULT_SCALE_BACK_POST_ENCODE_CRF = 17

all_video_filters = [
    # For media degradation, downscaling is an excellent operation.

    Filter(
        name = "scale",

        parameters = [
            # TODO : add ability to randomize the scale factor on each pass
            # (and adjust the to-be rescale factor(s) to match)

            ParserArgument(
                name = "factor",
                type = float,
                default = DEFAULT_SCALE_FACTOR
            ),
        ],

        filter_string = lambda: (
            filter_join(
                (
                    f"scale=iw/{runtime_value('scale_factor')}:"
                    f"ih/{runtime_value('scale_factor')}"
                ),
                h264_pad_filter
            )
        ),

        active_condition = is_not_dedicated_rescale_pass
    ),

    # There are two types of rescale when it comes to degradation :

    # 1. Pre-encode rescale, which immediately follows downscale in the same filterchain,
    # Prior to video encoding.
    # This creates noisy, visible "hyperpixels".

    Filter(
        name = "scale_back_pre_encode",
        special_shorthand = "sbe",

        requires_explicit_enabling = True,

        filter_string = lambda: filter_join(
            (
                f"scale=iw*{runtime_value('scale_factor')}:"
                f"ih*{runtime_value('scale_factor')}"
            ),
            h264_pad_filter
        ),

        active_condition = lambda: (
            not is_enabled_at_runtime("scale_back_post_encode")
            and
            is_not_dedicated_rescale_pass
        )
    ),

    # 2. Isolated rescale on a previously encoded video.
    # This magnifies the artifacts of the encoded H264 frame,
    # And tends to create a "shapely", "blurry", "glossy" effect, as opposed to blocky.

    # TODO : make these two mutually exclusive !

    # TODO : add a "rescale factor" ; only partially rescale
    # TODO : actually, maybe one for w and h separately...

    Filter(
        name = "scale_back_post_encode",
        special_shorthand = "sbo",

        requires_explicit_enabling = True,

        parameters = [
            # For isolated rescale to work, it must operate at high fidelity,
            # That is, with a low CRF, contrary to the rest of the filterchain.
            # Therefore it has its own CRF parameter.

            ParserArgument(
                name = "crf",
                special_shorthand = "crf",
                type = int,
                default = DEFAULT_SCALE_BACK_POST_ENCODE_CRF
            )

            # lower values, of course, lead to higher file sizes, but also...
            # to different types of artifact :
            # for instance, on test videos, 17 preserves mouths but 1 doesn't!
        ],

        filter_string = lambda: filter_join(
            (
                f"scale=iw*{runtime_value('scale_factor')}:"
                f"ih*{runtime_value('scale_factor')}"
            ),
            h264_pad_filter
        ),

        # Note that because is_dedicated_rescale_pass includes the enabling of sbo,
        # And sbo is explicit-enable only,
        # That means we're doing is_enabled("sbo") and is_enabled("sbo"),
        # Through the filter class's __post_init__().
        # Oh well!

        active_condition = is_dedicated_rescale_pass
    ),

    Filter(
        name = "blur",
        default_priority = 1,

        parameters = [
            ParserArgument(
                name = "sigma",
                special_shorthand = "sg",
                type = float
            )
        ],

        filter_string = lambda: (
            f"gblur=sigma={runtime_value('blur_sigma')}"
        ),

        active_condition = is_not_dedicated_rescale_pass
    ),

    Filter(
        name = "noise",
        special_shorthand = "e", # E. E. E. EE..E.E.EEEE..
        default_priority = 1,

        parameters = [
            # TODO : randomize noise strength on each pass

            ParserArgument(
                name = "strength",
                special_shorthand = "",
                default = DEFAULT_NOISE_STRENGTH
            )
        ],

        filter_string = lambda: (
            f"noise=alls={runtime_value('noise_strength')}:allf=t"
        ),

        active_condition = lambda: (
            is_not_dedicated_rescale_pass()
            and
            runtime_value("noise_strength") > 0 # TODO : is this neeeded ?
            # doesn't a 0-strength filter just do nothing, like blur ?
        )
    ),
]

all_audio_filters = [
    Filter(
        name = "volume",

        parameters = [
            # Low bitrates can lead to HEAVY clipping after multiple passes.
            # Users should lower the volume if they care for their ears !

            ParserArgument(
                name = "percentage",
                special_shorthand = "",
                type = float,
                default = DEFAULT_VOLUME_PERCENTAGE
            )
        ],

        filter_string = lambda: (
            f"volume=volume={runtime_value('volume_percentage')}"
        ),

        active_condition = is_not_dedicated_rescale_pass
    )
]

all_gif_filters = [
    Filter(
        name = "palette",

        parameters = [
            ParserArgument(
                name = "size",
                special_shorthand = "",
                default = DEFAULT_GIF_PALETTE_SIZE
            )
        ],

        filter_string = lambda: (
            f"split[s0][s1];"
            f"[s0]palettegen=max_colors={gif_palette_size}:stats_mode=diff[p];"
            f"[s1][p]paletteuse=dither=none"
        ),

        active_condition = lambda: is_gif(runtime_value("output"))
    )
]

all_filters = all_video_filters + all_audio_filters + all_gif_filters

# TODO : ...since we're doing Fascinate 2, let's just. Go all the way,
# And move the filter_strings in an impl/ subdir.
# The Filter class can just call them with the list of args, like Fascinate does.
# It will declutter the declaration.

def register_filters(parser):
    for filter in all_filters:
        filter.add_to_parser(parser)

def get_video_filters_for_pass():

    all_video_filters_by_priority = priority_sort(all_video_filters)

    return filter_join(*[
        filter()
        for filter in all_video_filters_by_priority
    ])

def get_audio_filters_for_pass():

    all_audio_filters_by_priority = priority_sort(all_audio_filters)

    return filter_join(*[
        filter()
        for filter in all_audio_filters_by_priority
    ], for_audio = True)

def get_gif_filters_for_pass():

    all_gif_filters_by_priority = priority_sort(all_gif_filters)

    return filter_join(*[
        filter()
        for filter in all_gif_filters_by_priority
    ])
