import collections

class Atom(Exception):

    def __init__(self, *args):
        if args:
            if len(args) > 1:
                self.payload = args
            else:
                self.payload = args[0]


def new_atom(atom):
    return type(atom, (Atom,), {})

def make_sequence(element):
    if not isinstance(element, collections.Iterable):
        return (element, )
    elif not isinstance(element, tuple):
        return tuple(element)
    return element

def typecheck(payload, types):
    for arg, type in zip(make_sequence(payload), make_sequence(types)):
        if not isinstance(payload, type):
            if type:
                raise TypeError('{} must be of type {}'.format(payload, type))


def dispatch(entity_map):
    atom_map = {}
    for entity in entity_map:
        if isinstance(entity, str):
            atom_map[entity] = entity_map[entity]
        else:
            for atom in entity:
                atom_map[atom] = entity_map[entity]

    def inner_wrapper(func):
        def wrapped(self, *args, **kwargs):
            try:
                func(self, *args, **kwargs)
            except Exception as exc:
                exc_name = exc.__class__.__name__
                if exc_name in atom_map:
                    route = atom_map[exc_name]
                    if isinstance(route, tuple):
                        typecheck(exc.payload, route[1])
                        route = route[0]
                        args = args + make_sequence(exc.payload)
                    else:
                        args = ()
                    dispatch(entity_map)(self.__class__.evaluate_msg)(self, route, *args)
                else:
                    raise exc
        return wrapped
    return inner_wrapper


class Atoms:

    def __init__(self, *atoms):
        self.atoms = []
        for atom in atoms:
            new_obj = new_atom(atom)
            setattr(self, atom, new_obj)
            self.atoms.append(atom)


class Actor:

    atoms = []

    def __init__(self):
        self.namespace = None
        for atom in self.atoms:
            new_obj = new_atom(atom)
            setattr(self, atom, new_obj)

    def register(self, namespace):
        self.namespace = namespace
        namespace.atoms.extend(self.atoms)

    def pass_atom(self, atom, *args):
        raise getattr(self, atom)(*args)

    def evaluate_msg(self, msg, *args, **kwargs):
        if msg in self.namespace.atoms:
            self.pass_atom(msg)
        elif isinstance(msg, str):
            getattr(self, msg)(*args, **kwargs)
        else:
            msg(*args, **kwargs)

    def pass_if(self, cond, true_atom, false_atom=None):
        if cond:
            self.evaluate_msg(true_atom)
        elif false_atom:
            self.evaluate_msg(false_atom)
