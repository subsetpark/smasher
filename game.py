from atoms import AtomPasser, atom_try
import random

class SimpleGame(AtomPasser):
    atoms = ['Correct', 'Wrong', 'Win']

    def __init__(self):
        super().__init__()
        self.points = 0
        self.number = random.choice(range(10))
        print(self.number)
    
    @atom_try({'Correct': lambda: print('Good job!')})
    def play_a_game(self):
        self.take_a_guess()

    @atom_try({('Wrong', 'ValueError', 'Again'): 'take_a_guess'})
    def take_a_guess(self):
        guess = input('Take a guess: ')
        self.check(int(guess) == self.number, 'Wrong', 'Correct')

if __name__ == '__main__':
    g = SimpleGame()
    g.play_a_game()
