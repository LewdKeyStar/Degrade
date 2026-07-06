from src.state.store import runtime_value, is_enabled_at_runtime

def is_dedicated_rescale_pass():
    return (
        is_enabled_at_runtime("scale_back_post_encode")
        and
        runtime_value("current_pass_number") == runtime_value("passes") - 1
    )

def is_not_dedicated_rescale_pass():
    return not is_dedicated_rescale_pass()
    
