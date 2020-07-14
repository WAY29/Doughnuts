from libs.config import alias, custom_set


@alias(True, k="key", v="value")
def run(key: str, *value):
    """
    set

    Set variable, use #{varname} to use it.
    """
    if (len(value) > 1):
        value = ' '.join(str(v) for v in value)
    else:
        value = value[0]
    custom_set(str(key), value)
