from atoms import AtomPasser, atom_try
import random


class SimpleGame(AtomPasser):
    atoms = ['Correct', 'Wrong', 'Win', 'KeepGoing', 'Done']

    def __init__(self):
        super().__init__()
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
        self.check(int(guess) == self.number, 'Wrong', 'Correct')

    def correct(self):
        self.points += 1
        self.check(self.points >= 5, 'KeepGoing', 'Done')

if __name__ == '__main__':
    g = SimpleGame()
    g.play_a_game()
