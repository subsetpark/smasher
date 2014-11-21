from atoms import Actor, atom_try, Atoms
import random


class SimpleGame(Actor):
    atoms = ['Correct', 'Wrong', 'Win', 'KeepGoing', 'Done']

    def __init__(self, a):
        super().__init__(a)
        self.points = 0

    def play_a_game(self):
        self.number = random.choice(range(10))
        print(self.number)
        self.take_a_guess()

    @atom_try({('Wrong', 'ValueError', 'Again'): 'take_a_guess',
               'Correct': 'correct',
               'KeepGoing': 'play_a_game',
               'Done': lambda: print('Good job!')})
    def take_a_guess(self):
        guess = input('Take a guess: ')
        self.pass_if(int(guess) == self.number, 'Wrong', 'Correct')

    def correct(self):
        self.points += 1
        self.pass_if(self.points >= 5, 'KeepGoing', 'Done')

if __name__ == '__main__':
    a = Atoms()
    g = SimpleGame(a)
    g.play_a_game()