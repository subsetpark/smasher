import builtins
from utils import make_sequence


class Atom(Exception):

    def __init__(self, *args):
        if args:
            if len(args) > 1:
                self.payload = args
            else:
                self.payload = args[0]


class AtomError(Exception):
    pass


def new_atom(atom, origin=None):
    cls = type(atom, (Atom,), {})
    if origin is not None:
        cls.__module__ = origin.__class__.__name__ # Is this kosher?
    return cls


def typecheck(payload, types):
    for arg, desired_type in zip(make_sequence(payload), make_sequence(types)):
        if desired_type:
            if not isinstance(payload, desired_type):
                raise TypeError('Type mismatch for {}: got {}, excpected {}'.format(payload, type(5), desired_type))


def dispatch(entity_map):
    """
    This is the dispatch decorator designed 
    to be used on Actor methods.
    """
    # Build list of atom names we're looking for
    atom_map = {}
    for entity in entity_map:
        if isinstance(entity, str):
            atom_map[entity] = entity_map[entity]
        else:
            for atom in entity:
                atom_map[atom] = entity_map[entity]

    def inner_wrapper(func):
        def wrapped(self, *args, **kwargs):
            # Validate dispatch
            dispatch_map = {self.get_atom(atom_name): value for atom_name, value in atom_map.items()}
            try:
                func(self, *args, **kwargs)
            except tuple(dispatch_map.keys()) as exc:
                route = dispatch_map[exc.__class__]
                if isinstance(route, tuple):
                    typecheck(exc.payload, route[1])
                    route = route[0]
                    args = args + make_sequence(exc.payload)
                else:
                    args = ()
                dispatch(entity_map)(self.__class__.evaluate_msg)(self, route, *args)
        return wrapped
    return inner_wrapper


class Atoms:

    def __init__(self, *atoms):
        self.atom_names = []
        self.globals = {}
        for atom in atoms:
            new_class = new_atom(atom)
            self.atom_names.append(atom)
            self.globals[a] = new_class


class Actor:

    atoms = []
    initialize_map = {}

    def __init__(self):
        self.atom_map = {}
        self.namespace = None
        if not self.initialize_map.get(self.__class__):
            for atom in self.atoms:
                new_class = new_atom(atom, origin=self)
                self.atom_map[atom] = new_class
            self.initialize_map[self.__class__] = True
        print('{}, {}'.format(self.__class__.__name__, self.atom_map))

    def register(self, namespace):
        self.namespace = namespace
        namespace.atom_names.extend(self.atoms)
        namespace.globals.update({a: self.atom_map[a] for a in self.atoms})

    def get_atom(self, atom_name):
        if atom_name in self.namespace.atom_names:
            return self.namespace.globals[atom_name]
        try:
            builtin = getattr(builtins, atom_name)
            if issubclass(builtin, Exception):
                return builtin
        except AttributeError:
            raise AtomError('Atom {} not found.'.format(atom_name))

    def pass_atom(self, atom_name, *args):
        raise self.atom_map[atom_name](*args)

    def evaluate_msg(self, msg, *args, **kwargs):
        if msg in self.atoms:
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
