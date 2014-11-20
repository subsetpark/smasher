class Atom(Exception):
    pass

def new_atom(atom):
    return type(atom, (Atom,), {})

def atom_try(entity_map):
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
                    self.evaluate_msg(route)
                else:
                    raise exc
        return wrapped
    return inner_wrapper

def atom_raise(atom):
    raise atom()

class AtomPasser:
    def __init__(self):
        self.current_atom = None
        for atom in self.atoms:
            new_obj = new_atom(atom)
            setattr(self, atom, new_obj)

    def pass_atom(self, atom):
        self.current_atom = getattr(self, atom)
        raise self.current_atom()

    def evaluate_msg(self, msg):
        if msg in self.atoms:
            self.pass_atom(msg)
        elif isinstance(msg, str):
            getattr(self, msg)()
        else:
            msg()

    def reraise(self):
        raise self.current_atom()

    def check(self, cond, false_atom, true_atom=None):
        if not cond:
            self.evaluate_msg(false_atom)
        if true_atom:
            self.evaluate_msg(true_atom)

class Atoms:
    def __init__(self, *atoms):
        for atom in atoms:
            new_obj = new_atom(atom)
            setattr(self, atom, new_obj)