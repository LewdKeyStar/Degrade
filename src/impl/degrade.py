from ffmpy import FFmpeg

from os import remove
from shutil import copyfile

from src.utils.filter_utils import filter_join
from src.utils.name_utils import add_suffix, is_gif, force_mp4

def degrade(
    input_path,
    output_path,

    crf,

    scale_factor,
    scale_back_pre_encode,
    scale_back_post_encode,
    scale_back_post_encode_crf,

    passes,

    noise_strength,
    blur_sigma,

    audio_bitrate,
    volume,

    gif_palette_size
):

    to_gif = is_gif(output_path)

    video_output_path = (
        output_path if not to_gif
        else force_mp4(output_path)
    )

    if scale_back_post_encode:
        passes += 1 # we need an extra pass just for the rescale if it should happen separately.

    for i in range(passes):

        # Denotes whether this is a pass dedicated to an isolated rescale (post-encode),
        # As opposed to a rescale happening pre-encoding with scale.
        # In that case, the CRF will be different and only the rescale filter is called.
        is_dedicated_rescale_pass = scale_back_post_encode and i == passes - 1

        # TODO : put those filter decls somewhere else...
        #  ...this is gonna end up with me creating decl types,
        # and a namespace,
        # and iteration over it...
        # I can't escape that

        noise_filter = (
            f"noise=alls={noise_strength}:allf=t"
            if noise_strength > 0
            else ""
        )

        blur_filter = (
            f"gblur=sigma={blur_sigma}"
        )

        volume_filter = f"volume=volume={volume}"

        # This is mandatory for libx264 encoding! It doesn't tolerate odd dimensions.
        # TODO : move it to filter_utils..?
        # It's not a proper filter like the others, just a suffix to scaling

        pad_filter = f"pad=ceil(iw/2)*2:ceil(ih/2)*2"

        # TODO : add interlacing option

        scale_filter = filter_join(
            f"scale=iw/{scale_factor}:ih/{scale_factor}",
            pad_filter
        )

        inverse_scale_filter_expression = f"scale=iw*{scale_factor}:ih*{scale_factor}"

        if (
            scale_back_pre_encode
            or
            scale_back_post_encode and i == passes - 1 # <=> dedicated rescale pass
            or
            not scale_back_post_encode and i < passes - 1
        ):
            inverse_scale_filter = filter_join(
                inverse_scale_filter_expression,
                pad_filter
            )
        else:
            inverse_scale_filter = ""

        video_filters = (
            [blur_filter, noise_filter, scale_filter, inverse_scale_filter]
            if not is_dedicated_rescale_pass
            else [inverse_scale_filter]
        )

        audio_filters = [volume_filter]

        pass_input_path = (
            input_path if i == 0
            else copyfile(video_output_path, add_suffix(video_output_path, "input"))
        )

        video_command = FFmpeg(
            global_options = "-y",
            inputs = {pass_input_path: None},
            outputs = {
                video_output_path: [
                    "-c:v", "libx264",
                    "-crf", f'''{
                        crf if not is_dedicated_rescale_pass
                        else scale_back_post_encode_crf
                    }''',

                    "-c:a", "aac", # tests used libopus, but FFMPEG only supports it w/ .mp4
                    "-b:a", f"{audio_bitrate}k",

                    "-vf", filter_join(*video_filters),
                    "-af", filter_join(*audio_filters)
                ]
            }
        )

        # print(video_command.cmd)

        video_command.run()

        if i > 0:
            remove(pass_input_path)

    if not to_gif:
        return

    palette_filter = (
        f"split[s0][s1];"
        f"[s0]palettegen=max_colors={gif_palette_size}:stats_mode=diff[p];"
        f"[s1][p]paletteuse=dither=none"
    )

    gif_command = FFmpeg(
        global_options = "-y",
        inputs = {video_output_path: None},
        outputs = {
            output_path: [
                "-vf", palette_filter
            ]
        }
    )

    gif_command.run()

    remove(video_output_path)
