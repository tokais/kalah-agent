from __future__ import print_function
import sys
sys.path.append('..')
from Game import Game
from KalahLogic import Board
import numpy as np

"""
Game class implementation for the game of Kalah.
Based on the OthelloGame then getGameEnded() was adapted to new rules.

Based on the OthelloGame by Surag Nair.
"""
class KalahGame(Game):
    def __init__(self, state="<8,0,0,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8>"):
        self.board = Board.parse(state)

    def getInitBoard(self):
        # return initial board (numpy board)
        return np.array(self.board.north_pits + [self.board.north] + self.board.south_pits + [self.board.south])

    def getBoardSize(self):
        # (a,b) tuple
        return (2, len(self.board.north_pits) + 1)

    def getActionSize(self):
        # return number of actions aka number of pits
        return len(self.board.north_pits)
    
    def numpyToBoard(self, board):
        # convert numpy board to Board object
        return Board(board[0], board[9],board[1:9], board[10:18])

    def getNextState(self, board, player, action):
        # if player takes action on board, return next (board,player)
        # action must be a valid move
        self.board = self.numpyToBoard(board)
        state, again = self.board.sow(player, action)
        self.board = state
        if not again:
            player = -player
        
        return (self.board.asnumpy(np.float64), player)



    def getValidMoves(self, board, player):
        # return a fixed size binary vector
        self.board = self.numpyToBoard(board)
        valids = self.board.get_legal_moves(player)
        valid_mask = [1 if i in valids else 0 for i in range(len(self.board.north_pits))]
        return np.array(valid_mask)

    def getGameEnded(self, board, player):
        # return 0 if not ended, 1 if player 1 won, -1 if player 1 lost
        # player = 1
        self.board = self.numpyToBoard(board)
        player = player + 1 # 1 -> 2, -1 -> 0
        if self.board.is_final():
            if (self.board[player] > self.board[not player]):
                return 1
            elif (self.board[player] < self.board[not player]):
                return -1
            else:
                return 1e-4 
            
        return 0        
    

    def getCanonicalForm(self, board, player):
        # return state if player==1, else return -state if player==-1

        return board

    def getSymmetries(self, board, pi):
        # cannot create symmetries for Kalah

        return board, pi

    def stringRepresentation(self, board):
        # 8x8 numpy array (canonical board)
        return str(board)

    @staticmethod
    def display(board):
        print(str(board))   