import subprocess

def get_integrated_loudness(input):
    ffmpeg_process = subprocess.run(
        (
            f"ffmpeg -i {input} "
            f"-af ebur128 " # measure loudness
            f"-f null - " # with no video output (which would just duplicate input).
            f"2>&1 > /dev/null " # The resulting logs are in stderr, so redirect,
            f"| grep \"I:   \" | tr -d ' '" # then search for integrated loudness line and remove whitespace.
        ),

        # ("I:" would match every line ; "I:    " only matches the final value)

        shell = True,
        capture_output = True,
        text = True
    )

    # The resulting string should be of the form : "I:-XX.XLUFS".
    # If not, this means there was no audio stream to begin with,
    # So just return None to signal it.

    if len(ffmpeg_process.stdout.split(":")) == 1:
        return None

    # Else, we isolate the float value, remove the newline and unit, and return.

    return float(
        ffmpeg_process.stdout.split(":")[1].strip().removesuffix("LUFS")
    )
