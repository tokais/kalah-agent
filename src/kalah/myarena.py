from Arena import Arena
from KalahGame import KalahGame as Game
from KalahLogic import Board, connect
from src.utils import *
from MCTS import MCTS  
from minimax_agent_vince_ordered_moves import minmax_agent
from minmax_tobi import agent as minmax_agent_tobi
import time
import multiprocessing
from src.kalah.pytorch.NNetWrapper import NNetWrapper as nn
import numpy as np

NORTH = True
SOUTH = not NORTH

BOARD = Board.parse("<8,0,0,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8>")


args = dotdict({
    'numIters': 1000,
    'numEps': 1,              # Number of complete self-play games to simulate during a new iteration.
    'tempThreshold': 15,        #
    'updateThreshold': 0.6,     # During arena playoff, new neural net will be accepted if threshold or more of games are won.
    'maxlenOfQueue': 200000,    # Number of game examples to train the neural networks.
    'numMCTSSims': 4000,          # Number of games moves for MCTS to simulate.
    'arenaCompare': 40,         # Number of games to play during arena play to determine if new net will be accepted.
    'cpuct': 1,

    'checkpoint': './temp/',
    'load_model': False,
    'load_folder_file': ('./temp','temp.pth.tar'),
    'numItersForTrainExamplesHistory': 20,

})

class player_move:
    def __call__(self, board:Board):
        '''simulates player move
            returns new tree and new state'''
        mymove = None
        side = NORTH
        while mymove == None :
            try:
                mymove = input("Choose your move: ")
                mymove = int(mymove) - 1
            except:
                if mymove == "q":
                    exit(1)
                mymove = None
                print("not a number")
                continue
            if mymove < 0 or mymove >= len(board.north_pits) or not board.is_legal(side, mymove):
                mymove = None
                print("not a legal move")
                continue
        return mymove
    
    def notify(self, board:Board, action):
        print(f"Opponent chose: {action+1}")

class minmax_move:
    def __init__(self, move_time = 3):
        self.move_time = move_time
               
    def __call__(self, board:Board):
        '''dont need to rerun bc arena handles again moves'''
        
        side = NORTH
        best_move = -1
        end = time.time() + self.move_time  

        # for move in minmax_agent(board, side=NORTH, max_player_side=NORTH):
        for move in minmax_agent_tobi(board):
            if time.time() > end:
                break
            print(best_move, end=",")
            if move != best_move:
                best_move = move
        return best_move


class alpha_zero_move:
    def __init__(self, filename='best.pth.tar'):
        self.filename = filename
        g = Game()
        nnet = nn(g)
        nnet.load_checkpoint(folder="best_models", filename=self.filename)
        self.nmcts = MCTS(g, nnet, args)
        
    def __call__(self, board:Board):
        return self.get_move(board).__next__()

    def get_move(self, board:Board):

        board.active_player = -1
        print(board)
        best_move = -1
        for depth in [2000, 2500, 3000, 3500, 4000]:
            move = np.argmax(self.nmcts.getInstantActionProb(board, depth, temp=0))
            if move != best_move:
                best_move = move
                print(f"I move {move+ 1}")
                print(board.sow((board.active_player+1)//2, move)[0])
            yield move.item()

    def notify(self, board:Board, action):
        print(f"Opponent chose: {action+1}")



def main():
    g = Game()
    arena = Arena(player1=minmax_move(move_time=3), 
                player2=alpha_zero_move(filename='best_64.pth.tar'),
                game=g, 
                display=g.display)
    
    minmax_wins, alpha_zero_wins, draws = arena.playGames(2, verbose=True)
    print("minmax_wins", minmax_wins)
    print("alpha_zero_wins", alpha_zero_wins)
    print("draws", draws)



# if __name__ == "__main__": 
#     main()
    # board = BOARD
    # for move in alpha_zero_move(board):
    #     print(move)



if __name__ == "__main__":
    with multiprocessing.Manager() as manager:
        calculated_states = manager.dict()
        host = "wss://kalah.kwarc.info/socket" #if os.getenv("USE_WEBSOCKET") else "localhost"
        token = 'Miaumiau'
        connect(alpha_zero_move(filename='best_64.pth.tar').get_move, host=host, token=token, name='alphadude', debug=True)

    
