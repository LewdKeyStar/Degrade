def filter_join(*filters):
    return ",".join(filters).removeprefix(",").removesuffix(",").replace(",,", ",")
