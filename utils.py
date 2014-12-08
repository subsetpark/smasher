import collections

def make_sequence(element):
    if not isinstance(element, collections.Iterable):
        return (element, )
    elif not isinstance(element, tuple):
        return tuple(element)
    return element