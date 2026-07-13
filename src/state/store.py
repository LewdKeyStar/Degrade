from argparse import Namespace

# YOINK from Fascinate!

class SubscriptableNamespace:

    def __init__(self, namespace):

        self.temp_namespace = None

    def __enter__(self):
        global global_namespace

        if not isinstance(global_namespace, dict):

            global_namespace = vars(global_namespace)

        return global_namespace

    def __exit__(self, exception_type, exception_val, traceback):

        global global_namespace

        if isinstance(global_namespace, dict):

            global_namespace = Namespace(**global_namespace)

def init_state():
    global global_namespace
    global_namespace = Namespace()

def runtime_value(key, *, numerize_bool = False):

    with SubscriptableNamespace(global_namespace) as ns:

        if key not in ns:
            raise KeyError(
                f"Attempted access to key {key} which was never registered in store."
            )

        val = ns[key]

        # Pass an int for filters that treat their booleans as such.
        # Technically, the one option this has been tested with (scale.interl)
        # Also works with the bool string...but let's not tempt fate.

        if numerize_bool:

            val = 1 if ns[key] else 0

        return val

# Boolean truth value alias.

def is_enabled_at_runtime(key):
    return runtime_value(key)

def override_runtime_value(key, new_value):

    with SubscriptableNamespace(global_namespace) as ns:

        if key not in ns:
            raise KeyError(
                f"Attempted to override runtime value of nonexistent store entry {key}."
            )

        ns[key] = new_value

def add_to_runtime(key, value):

    with SubscriptableNamespace(global_namespace) as ns:

        if key in ns:
            raise ValueError(
                f"Attempted to add key {key} to store, which was already present."
                "Use override_runtime_value instead."
            )

        ns[key] = value
