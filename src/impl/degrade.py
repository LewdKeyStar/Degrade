from ffmpy import FFmpeg

from os import remove
from shutil import copyfile

from src.utils.filter_utils import filter_join
from src.utils.name_utils import (
    add_suffix,

    is_gif, is_still_image, is_h264_incompatible,

    force_mp4
)
from src.utils.loudness_utils import get_integrated_loudness

from src.decl.filters import (
    get_video_filters_for_pass,
    get_audio_filters_for_pass,
    get_gif_filters_for_pass
)

from src.state.store import (
    runtime_value,
    is_enabled_at_runtime,
    override_runtime_value,
    add_to_runtime
)

h264_incompatible_formats = [ "webm" ]

def degrade_video():

    to_gif = is_gif(runtime_value("output"))
    to_still_image = is_still_image(runtime_value("output"))

    to_image = to_gif or to_still_image
    to_video = not to_image

    video_output_path = (
        force_mp4(runtime_value("output"))
        if to_image or is_h264_incompatible(runtime_value("output"))
        else runtime_value("output")
    )

    if is_enabled_at_runtime("scale_back_post_encode"):
        override_runtime_value(
            "passes",
            runtime_value("passes") + 1
            # we need an extra pass just for the rescale if it should happen separately.
        )

    add_to_runtime("current_pass_number", 0)

    for i in range(runtime_value("passes")):

        override_runtime_value("current_pass_number", i)

        # Denotes whether this is a pass dedicated to an isolated rescale (post-encode),
        # As opposed to a rescale happening pre-encoding with scale.
        # In that case, the CRF will be different and only the rescale filter is called.
        is_dedicated_rescale_pass = (
            runtime_value("scale_back_post_encode") and
            i == runtime_value("passes") - 1
        )

        video_filters = get_video_filters_for_pass()

        audio_filters = get_audio_filters_for_pass()

        pass_input_path = (
            runtime_value("input") if i == 0
            else copyfile(video_output_path, add_suffix(video_output_path, "input"))
        )

        video_command = FFmpeg(
            global_options = "-y -hide_banner",
            inputs = {pass_input_path: None},
            outputs = {
                video_output_path: [
                    "-c:v", "libx264",
                    "-crf", f'''{
                        runtime_value("crf") if not is_dedicated_rescale_pass
                        else runtime_value("scale_back_post_encode_crf")
                    }''',

                    "-c:a", "aac", # tests used libopus, but FFMPEG only supports it w/ .mp4
                    "-b:a", f"{runtime_value('audio_bitrate')}k",

                    "-vf", video_filters,
                    "-af", audio_filters
                ]
            }
        )

        if is_enabled_at_runtime("print_commands"):
            print(video_command.cmd)

        video_command.run()

        # after each pass, remove the input, except if :

        if not (
            # this was the first pass (where the input is the original file)
            i == 0
            or
            # this is the last pass with a video output
            # in which case it requires loudness normalization,
            # so we leave the _input copy alone to serve as the input for that.
            ((i == runtime_value("passes") - 1) and to_video)
        ):
            remove(pass_input_path)

    if to_gif:

        gif_filters = get_gif_filters_for_pass()

        gif_command = FFmpeg(
            global_options = "-y -hide_banner",
            inputs = {video_output_path: None},
            outputs = {
                runtime_value("output"): [
                    "-vf", gif_filters
                ]
            }
        )

        if is_enabled_at_runtime("print_commands"):
            print(gif_command.cmd)

        gif_command.run()

    elif to_still_image:

        still_image_command = FFmpeg(
            global_options = "-y -hide_banner",
            inputs = {video_output_path: None},
            outputs = {runtime_value("output"): [
                "-vf", "select='eq(n, 0)'",
                "-frames:v", "1", # FIXME : despite this line FFMPEG still issues a warning.
            ]}
        )

        if is_enabled_at_runtime("print_commands"):
            print(still_image_command.cmd)

        still_image_command.run()

    # Even basic video output requires another step :
    # Loudness normalization.
    # This is because low bitrates often lead to clipping,
    # ESPECIALLY with multiple passes.
    # The audio levels can become dangerously high with no safeguards ;
    # This prevents it.

    else:

        target_integrated_loudness = get_integrated_loudness(
            runtime_value("input")
        )

        if target_integrated_loudness is not None: # <=> if there is an audio stream at all

            loudness_normalisation_command = FFmpeg(
                global_options = "-y -hide_banner",
                inputs = {pass_input_path: None},
                outputs = {runtime_value("output"): [
                    "-c:v", "copy",
                    "-af", f"loudnorm=i={target_integrated_loudness}"
                ]}
            )

            if is_enabled_at_runtime("print_commands"):
                print(loudness_normalisation_command.cmd)

            loudness_normalisation_command.run()

    # If the final input is an image, remove the video that produced it.
    if to_image:
        remove(video_output_path)
    # Otherwise, the video IS the output, so we do not remove it ;
    # However, we do remove the input of the last pass,
    # Which was left behind for sound normalization to pick up.
    else:
        remove(pass_input_path)
