from kalah.Arena import Arena
from KalahGame import KalahGame as Game
from KalahLogic import Board, connect
from utils import *
from kalah.MCTS import MCTS  
from minimax_agent_vince_ordered_moves import minmax_agent
from minmax_tobi import agent as minmax_agent_tobi
import time
import multiprocessing
# multiprocessing.set_start_method("fork")



from pytorch.NNet import NNetWrapper as nn


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
    'numMCTSSims': 1000,          # Number of games moves for MCTS to simulate.
    'arenaCompare': 40,         # Number of games to play during arena play to determine if new net will be accepted.
    'cpuct': 1,

    'checkpoint': './temp/',
    'load_model': False,
    'load_folder_file': ('./temp','temp.pth.tar'),
    'numItersForTrainExamplesHistory': 20,

})


def player_move(board:Board):
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
       


def minmax_move(board:Board, move_time = 3):
    '''dont need to rerun bc arena handles again moves'''
    
    side = NORTH
    best_move = -1
    end = time.time() + move_time  

    # for move in minmax_agent(board, side=NORTH, max_player_side=NORTH):
    for move in minmax_agent_tobi(board):
        if time.time() > end:
            break
        print(best_move, end=",")
        if move != best_move:
            best_move = move
    return best_move


def alpha_zero_move(board:Board):
    g = Game()
    nnet = nn(g)
    nnet.load_checkpoint(folder="best_models", filename='best.pth.tar')
    nmcts = MCTS(g, nnet, args)
    print(board)
    for depth in [3000]:
        move = np.argmax(nmcts.getInstantActionProb(board, depth, temp=0))
        print(move)
        print(board.sow(NORTH, move)[0])
        yield move.item()

def main():
    g = Game()
    nnet = nn(g)
    nnet.load_checkpoint(folder="best_models", filename='best.pth.tar')
    # nnet.load_checkpoint(folder=args.checkpoint, filename='best.pth.tar')
    nmcts = MCTS(g, nnet, args)

    arena = Arena(player1=minmax_move, 
                player2=lambda x: np.argmax(nmcts.getActionProb(x, temp=0)),
                game=g, 
                display=lambda x: print(g.stringRepresentation(x)))
    
    arena.playGames(2, verbose=True)
        


# if __name__ == "__main__": 
#     # board = BOARD
#     # for move in alpha_zero_move(board):
#     #     print(move)
#     main()



if __name__ == "__main__":
    with multiprocessing.Manager() as manager:
        calculated_states = manager.dict()
        host = "wss://kalah.kwarc.info/socket" #if os.getenv("USE_WEBSOCKET") else "localhost"
        token = 'Miaumiau'
        connect(alpha_zero_move, host=host, token=token, name='alphadude')

    
