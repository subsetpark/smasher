smasher
=======

## Typed Exception-Based Message Passing for Python

At some point in the recent past, I found myself enjoying the process of 
creating my own exceptions for specific business logic needs at my Python 
day job. So, naturally, I thought: *what if you could use exceptions for
all control flow in Python?*

`smasher` applications have two main components: `Actor` objects that communicate 
with each other by way of raised exceptions, called `Atoms`, and the global `Atoms`
namespace.

Looking at an example, we see:

```py
class SimpleGame(Actor):
    atoms = ['Correct', 'Wrong', 'Win', 'KeepGoing', 'Done']
```

`Actor` classes declare their own atoms, which are instantiated as subclasses
of the `Atom` exception class. Actors catch atoms using the `dispatch` decorator:

```py
@dispatch({('Wrong', 'ValueError', 'Again'): 'take_a_guess',
           'Correct': 'correct',
           'KeepGoing': 'play_a_game',
           'Guess': ('evaluate', int)})
def take_a_guess(self):
    self.server.get_guess()
```

Here we see that the main locus for control flow is the `take_a_guess` method. If any
of the `Wrong`, `ValueError`, or `Again` exceptions are raised, we recurse; the `Correct`
and `KeepGoing` atoms are routed to the appropriate methods; finally, we see that the 
`Guess` atom is expected to contain a single element, an int, which will be passed to
the `evaluate` method. Atoms can also be dispatched to raw lambdas or even other atoms, 
though in practice it will usually suffice simply to catch the original signal further up.
