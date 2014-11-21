from atoms import Actor, dispatch, Atoms
import random


class SimpleGame(Actor):
    atoms = ['Correct', 'Wrong', 'Win', 'KeepGoing', 'Done']

    def __init__(self, server):
        super().__init__()
        self.points = 0
        self.server = server

    def play_a_game(self):
        self.number = random.choice(range(10))
        print(self.number)
        print('Points: {}'.format(self.points))
        self.take_a_guess()

    @dispatch({('Wrong', 'ValueError', 'Again'): 'take_a_guess',
               'Correct': 'correct',
               'KeepGoing': 'play_a_game'})
    def take_a_guess(self):
        guess = self.server.get_guess()
        self.pass_if(int(guess) == self.number, 'Correct', 'Wrong')

    def correct(self):
        self.points += 1
        self.pass_if(self.points >= 5, 'Done', 'KeepGoing')

class Alphonse(Actor):
    atoms = ['NewGame', 'Finished']

    def __init__(self):
        super().__init__()
        self.plays = 0

    def guess(self):
        return random.choice(range(10))

    def start(self):
        print('now starting. {}'.format(self.plays))
        self.pass_if(self.plays >= 3, 'Finished', 'NewGame')

class Server(Actor):

    def __init__(self, player):
        super().__init__()
        self.player = player
        self.game = SimpleGame(self)

    def register(self, namespace):
        super().register(namespace)
        self.game.register(namespace)

    def get_guess(self):
        return self.player.guess() # TODO: Raise with values

    @dispatch({'NewGame': 'new_game',
               'Done': 'run',
               'Finished': lambda: print('Good job!')})
    def run(self):
        self.player.start()

    def new_game(self):
        self.player.plays += 1
        self.game.points = 0
        self.game.play_a_game()

if __name__ == '__main__':
    a = Atoms()
    
    p = Alphonse()
    p.register(a)

    s = Server(p)
    s.register(a)
    
    s.run()