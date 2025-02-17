from __future__ import print_function
import sys
sys.path.append('..')
from Game import Game
from .KalahLogic import Board
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
        return np.array(self.board.north_pits + self.board.south_pits)

    def getBoardSize(self):
        # (a,b) tuple
        return (2, len(self.board.north_pits))

    def getActionSize(self):
        # return number of actions aka number of pits
        return len(self.board.north_pits)

    def getNextState(self, board, player, action):
        # if player takes action on board, return next (board,player)
        # action must be a valid move
        state, again = board.sow(player, action)
        if not again:
            player = -player
        
        return (state.north_pits + state.south_pits, player)



    def getValidMoves(self, board, player):
        # return a fixed size binary vector

        valids = board.get_legal_moves(player)
        valid_mask = [1 if i in valids else 0 for i in range(len(board.north_pits))]
        return np.array(valid_mask)

    def getGameEnded(self, board, player):
        # return 0 if not ended, 1 if player 1 won, -1 if player 1 lost
        # player = 1
        b = Board(self.n)
        b.pieces = np.copy(board)

        if b.is_win(player):
            return 1
        if b.is_win(-player):
            return -1
        if b.has_legal_moves():
            return 0
        # draw has a very little value 
        return 1e-4

    def getCanonicalForm(self, board, player):
        # return state if player==1, else return -state if player==-1
        return player*board

    def getSymmetries(self, board, pi):
        # mirror, rotational
        assert(len(pi) == self.n**2+1)  # 1 for pass
        pi_board = np.reshape(pi[:-1], (self.n, self.n))
        l = []

        for i in range(1, 5):
            for j in [True, False]:
                newB = np.rot90(board, i)
                newPi = np.rot90(pi_board, i)
                if j:
                    newB = np.fliplr(newB)
                    newPi = np.fliplr(newPi)
                l += [(newB, list(newPi.ravel()) + [pi[-1]])]
        return l

    def stringRepresentation(self, board):
        # 8x8 numpy array (canonical board)
        return board.tostring()

    @staticmethod
    def display(board):
        n = board.shape[0]

        print("   ", end="")
        for y in range(n):
            print (y,"", end="")
        print("")
        print("  ", end="")
        for _ in range(n):
            print ("-", end="-")
        print("--")
        for y in range(n):
            print(y, "|",end="")    # print the row #
            for x in range(n):
                piece = board[y][x]    # get the piece to print
                if piece == -1: print("X ",end="")
                elif piece == 1: print("O ",end="")
                else:
                    if x==n:
                        print("-",end="")
                    else:
                        print("- ",end="")
            print("|")

        print("  ", end="")
        for _ in range(n):
            print ("-", end="-")
        print("--")
