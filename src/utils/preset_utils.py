import json

def preset_file_to_args(preset_file_path):

    if preset_file_path is None:
        return [""]

    with open(preset_file_path) as preset_file:

        preset_json = json.load(preset_file)

    nested_preset_arg_string = [
        [key, preset_json[key]] if preset_json[key] != "" else [key]
        for key in preset_json
    ]

    preset_arg_string = (
        [""] # blank input name first, so it's not counted
        +
        [
            arg
            for nested_arg in nested_preset_arg_string
            for arg in nested_arg
        ]
    )

    return preset_arg_string
