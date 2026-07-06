from ffmpy import FFmpeg

from os import remove
from shutil import copyfile

from src.utils.filter_utils import filter_join
from src.utils.name_utils import add_suffix, is_gif, force_mp4

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

def degrade_video():

    to_gif = is_gif(runtime_value("output"))

    video_output_path = (
        runtime_value("output") if not to_gif
        else force_mp4(runtime_value("output"))
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
            global_options = "-y",
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

        # print(video_command.cmd)

        video_command.run()

        if i > 0:
            remove(pass_input_path)

    if not to_gif:
        return

    gif_filters = get_gif_filters_for_pass()

    gif_command = FFmpeg(
        global_options = "-y",
        inputs = {video_output_path: None},
        outputs = {
            output_path: [
                "-vf", gif_filters
            ]
        }
    )

    gif_command.run()

    remove(video_output_path)
