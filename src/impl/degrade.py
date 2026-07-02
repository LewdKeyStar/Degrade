from ffmpy import FFmpeg

from os import remove
from shutil import copyfile

from src.utils.filter_utils import filter_join
from src.utils.name_utils import add_suffix, is_gif, force_mp4

def degrade(
    input_path,
    output_path,

    crf,
    noise_strength,

    audio_bitrate,
    volume,

    scale_factor,
    rescale,

    passes,

    gif_palette_size
):

    to_gif = is_gif(output_path)

    video_output_path = (
        output_path if not to_gif
        else force_mp4(output_path)
    )

    noise_filter = (
        f"noise=alls={noise_strength}:allf=t"
        if noise_strength > 0
        else ""
    )

    volume_filter = f"volume=volume={volume}"

    # TODO : add interlacing option

    scale_filter = f"scale=iw/{scale_factor}:ih/{scale_factor}"

    # This is mandatory for libx264 encoding! It doesn't tolerate odd dimensions.

    pad_filter = f"pad=ceil(iw/2)*2:ceil(ih/2)*2"

    # ...but put it after scaling, of course.

    for i in range(passes):

        pass_input_path = (
            input_path if i == 0
            else copyfile(video_output_path, add_suffix(video_output_path, "input"))
        )

        inverse_scale_filter = (
            f"scale=iw*{scale_factor}:ih*{scale_factor}"
            if rescale or i < passes - 1
            else ""
        )

        video_command = FFmpeg(
            global_options = "-y",
            inputs = {pass_input_path: None},
            outputs = {
                video_output_path: [
                    "-c:v", "libx264",
                    "-crf", f"{crf}",

                    "-c:a", "aac", # tests used libopus, but FFMPEG only supports it w/ .mp4
                    "-b:a", f"{audio_bitrate}k",

                    "-vf", filter_join([
                        noise_filter, scale_filter, pad_filter, inverse_scale_filter
                    ]),
                    "-af", filter_join([
                        volume_filter
                    ])
                ]
            }
        )

        video_command.run()

        if i > 0:
            remove(pass_input_path)

    if not to_gif:
        return

    palette_filter = (
        "" if not is_gif(output_path)

        else (
            f"split[s0][s1];"
            f"[s0]palettegen=max_colors={gif_palette_size}:stats_mode=diff[p];"
            f"[s1][p]paletteuse=dither=none"
        )
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
