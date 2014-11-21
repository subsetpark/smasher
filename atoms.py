class Atom(Exception):
    pass


def new_atom(atom):
    return type(atom, (Atom,), {})


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
                    dispatch(entity_map)(self.__class__.evaluate_msg)(self, route)
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

    def pass_atom(self, atom):
        raise getattr(self, atom)()

    def evaluate_msg(self, msg):
        if msg in self.namespace.atoms:
            self.pass_atom(msg)
        elif isinstance(msg, str):
            getattr(self, msg)()
        else:
            msg()

    def pass_if(self, cond, true_atom, false_atom=None):
        if cond:
            self.evaluate_msg(true_atom)
        elif false_atom:
            self.evaluate_msg(false_atom)
