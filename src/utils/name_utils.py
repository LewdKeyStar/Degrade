from os.path import splitext

def add_suffix(input_name, suffix):

    root, ext = splitext(input_name)

    return f"{root}_{suffix}" + ext

def is_gif(input_name):
    return splitext(input_name)[1].lower() == ".gif"

def force_gif(output_name):
    return f"{splitext(output_name)[0]}.gif"

def force_mp4(output_name):
    return f"{splitext(output_name)[0]}.mp4"
