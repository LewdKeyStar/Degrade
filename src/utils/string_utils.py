def abbreviate(snake_name):
    return "".join([word[0] for word in snake_name.split("_")])

def to_kebab(snake_name):
    return snake_name.replace("_", "-")
