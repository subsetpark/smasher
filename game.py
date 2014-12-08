from atoms import Actor, dispatch
import random


class SimpleGame(Actor):
    atoms = ['Correct', 'Wrong', 'Win', 'KeepGoing', 'GameOver']

    def __init__(self, server):
        super().__init__()
        self.points = 0
        self.server = server

    def play_a_game(self):
        self.number = random.choice(range(10))
        print('Number to guess: {}'.format(self.number))
        print('Game points: {}'.format(self.points))
        self.take_a_guess()

    @dispatch({('Wrong', 'ValueError'): 'take_a_guess',
               'Correct': 'correct',
               'KeepGoing': 'play_a_game',
               'Guess': ('evaluate', int)})
    def take_a_guess(self):
        self.server.get_guess()

    def evaluate(self, guess):
        self.pass_if(int(guess) == self.number, 'Correct', 'Wrong')

    def correct(self):
        self.points += 1
        self.pass_if(self.points >= 5, 'GameOver', 'KeepGoing')


class Alphonse(Actor):
    atoms = ['Guess', 'NewGame', 'Finished']

    def __init__(self):
        super().__init__()
        self.plays = 0

    def guess(self):
        self.pass_atom('Guess', random.choice(range(10)))

    def start(self):
        self.plays += 1
        self.pass_if(self.plays > 3, 'Finished', 'NewGame')


class Server(Actor):

    def __init__(self, player):
        super().__init__()
        self.player = player
        self.game = SimpleGame(self)

    def register(self, namespace):
        super().register(namespace)
        self.game.register(namespace)

    def get_guess(self):
        self.player.guess()

    @dispatch({'NewGame': 'new_game',
               'GameOver': 'run',
               'Finished': lambda: print('Good job!')})
    def run(self):
        self.player.start()

    def new_game(self):
        print('Player starting a new game. play #{}.'.format(self.player.plays))
        self.game.points = 0
        self.game.play_a_game()


if __name__ == '__main__':
    p = Alphonse()
    s = Server(p)
    s.run()
