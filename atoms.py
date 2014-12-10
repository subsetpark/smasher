import builtins
from utils import make_sequence


class Atom(Exception):

    def __init__(self, *args):
        if args:
            self.payload = args

    def __str__(self):
        return '{}{}'.format(self.__class__.__name__, ': {}'.format(self.payload) if self.payload else '')

class AtomError(Exception):
    pass


def typecheck(payload, types):
    for arg, desired_type in zip(make_sequence(payload), make_sequence(types)):
        if desired_type:
            if not isinstance(arg, desired_type):
                raise TypeError('Type mismatch for {}: got {}, excpected {}'.format(repr(arg), type(arg), desired_type))

class Actor:
    atoms = []
    _initialize_map = {}
    _globals = {}
    _listeners = ()

    def __init__(self):
        self.atom_map = {}
        if not self._initialize_map.get(self.__class__):
            for atom in self.atoms:
                new_class = self.new_atom(atom)
                self.atom_map[atom] = new_class
            self._initialize_map[self.__class__] = True

    def new_atom(self, atom_name):
        if atom_name in self._globals:
            raise AtomError('{} could not create Atom {}; it already exists.'.format(self, atom_name))
        cls = type(atom_name, (Atom,), {})
        cls.__module__ = self.__class__.__name__  # Is this kosher?
        self._globals[atom_name] = cls
        return cls

    def get_atom(self, atom_name):
        if atom_name in self._globals:
            return self._globals[atom_name]
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
            self.pass_atom(msg, *args)
        elif isinstance(msg, str):
            getattr(self, msg)(*args, **kwargs)
        else:
            msg(*args, **kwargs)

    def pass_if(self, cond, true_atom, false_atom=None, args=()):
        if cond:
            self.evaluate_msg(true_atom, *args)
        elif false_atom:
            self.evaluate_msg(false_atom, *args)

    @staticmethod
    def dispatch(entity_map, listeners=()):
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
                        args = make_sequence(exc.payload)
                    else:
                        args = ()
                    self.dispatch(entity_map)(self.__class__.evaluate_msg)(self, route, *args)
            return wrapped
        return inner_wrapper