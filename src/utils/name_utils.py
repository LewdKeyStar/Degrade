from os.path import splitext

def add_suffix(input_name, suffix):

    root, ext = splitext(input_name)

    return f"{root}_{suffix}" + ext

def is_gif(input_name):
    return splitext(input_name)[1].lower() == ".gif"

def is_still_image(input_name):
    return splitext(input_name)[1].lower() in [
        ".png",
        ".jpg", ".jpeg", ".jfif",
        ".webp"
    ]

def is_h264_incompatible(input_name):
    return splitext(input_name)[1].lower() in [
        ".webm",
        # TODO : find the others !
    ]

def force_gif(output_name):
    return f"{splitext(output_name)[0]}.gif"

def force_mp4(output_name):
    return f"{splitext(output_name)[0]}.mp4"
