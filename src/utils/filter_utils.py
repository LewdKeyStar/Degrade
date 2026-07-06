import re

h264_pad_filter = f"pad=ceil(iw/2)*2:ceil(ih/2)*2"

def filter_join(*filters, for_audio = False):
    
    joined = re.sub(
        ",,+",
        ",",
        ",".join(filters)
    ).removeprefix(",").removesuffix(",")

    return (
        joined if joined != ""
        else (
            "null" if not for_audio
            else "anull"
        )
    )
