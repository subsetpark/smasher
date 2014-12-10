from atoms import Actor

class Calc(Actor):
    atoms = ['Plus', 'Minus', 'Squared', 'Result']

    @Actor.dispatch({'Plus': ('add', int, int),
                     'Minus': ('subtract', int, int),
                     'Result': ('display', int)})
    def calc(self):
        entry = input('> ')
        phrase = entry.split()
        x, y = int(phrase[0]), int(phrase[2])
        self.pass_if('+' in entry, 'Plus', args=(x, y))
        self.pass_if('-' in entry, 'Minus', args=(x, y))

    def result(self, val):
        self.pass_atom('Result', val)

    def minus(self, x, y):
        self.result(x - y)

    def add(self, x, y):
        self.result(x + y)

    def display(self, result):
        print('Here is your computation: {}'.format(result))

if __name__ == '__main__':
    Calc().calc()