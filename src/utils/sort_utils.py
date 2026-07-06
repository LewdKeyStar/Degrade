from src.state.store import runtime_value

def priority_sort(l):
    return list(
        sorted(
            l,
            key = lambda x: runtime_value(f"{x.name}_priority"),
            reverse = True
        )
    )
