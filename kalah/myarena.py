from Arena import Arena
from KalahGame import KalahGame as Game
from KalahLogic import Board
from utils import *
from MCTS import MCTS  
from minimax_agent_vince_ordered_moves import minmax_agent
# from minmax_tobi import agent as minmax_agent
import time

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
       


def minmax_move(board:Board, move_time = 100):
    '''simulates minmax move
        returns new tree and new state'''
    
    side = NORTH
    best_move = -1
    end = time.time() + move_time  
    again = True
    while again:
        again = False
        for move in minmax_agent(board, side=SOUTH, max_player_side=SOUTH):
        # for move in minmax_agent(board):
            if time.time() > end:
                break
            print(best_move, end=",")
            if move != best_move:
                best_move = move
                _, again = board.sow(side, best_move)
        if again:
            print("Need to Calculating another move ... (dont at moment)")
            again = False
    return best_move


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
        


if __name__ == "__main__":
    board = BOARD
    for move in minmax_agent(board, side=NORTH):    
        print(move)
        
    # main()
