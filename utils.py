def make_sequence(element):
    if not (isinstance(element, tuple) or isinstance(element, list)):
        return (element, )
    elif not isinstance(element, tuple):
        return tuple(element)
    return element