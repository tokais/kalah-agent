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
        self.stringState = state
        self.initial_board = Board.parse(state)

    def getInitBoard(self):
        """return initial board"""
        self.initial_board = Board.parse(self.stringState)
        return self.initial_board
    
    def getBoardSize(self):
        """Returns the board size of the game (pits plus kalah pit) * 2"""
        return (len(self.initial_board.north_pits) + 1, 2)

    def getActionSize(self):
        """return number of possible actions aka number of pits"""
        return len(self.initial_board.north_pits)
    
    def numpyToBoard(self, numpy_board):
        """convenience function to convert numpy board to Board object"""
        return Board(numpy_board[0], numpy_board[9],numpy_board[1:9], numpy_board[10:18])

    def getNextState(self, board:Board, player, action):
        """if player takes action on board, return next (board,player)"""
        state, again = board.execute_move(player, action)
        if not again:
            player = -player
        
        return (state, player)


    def getValidMoves(self, board:Board, player):
        """Get Valid moves for player and board
        returns:    a binary numpy vector of length self.getActionSize(),
                    1 for valid moves, 0 for the others"""
        # player is always 1??? when called from predict in NN

        valids = board.legal_moves((player+1)/2)
        valid_mask = [1 if i in valids else 0 for i in range(len(board.north_pits))]
        return np.array(valid_mask)

    def getGameEnded(self, board:Board, player):
        """Check if game has ended
        returns:   0 if not ended yet, 1 if player 1 won, -1 if player 1 lost, .0001 for draw"""
        # player = 1

        player = (player + 1)//2
        if board.is_final():
            if (board[player] > board[not player]):
                return 1
            elif (board[player] < board[not player]):
                return -1
            else:
                return 1e-4 
            
        return 0        
    

    def getCanonicalForm(self, board:Board, player):
        """returns always board
        in original idea should return board if player==1, else -board"""

        return board

    def getSymmetries(self, board:Board, pi):
        """Board gets flipped and pi gets reversed"""
        symBoard = Board(board.north, board.south, board.north_pits, board.south_pits)

        return symBoard, -pi

    def stringRepresentation(self, board):
        """needs to be unique for each player - is used for caching"""
        board_str = '-'.join(map(str, board.north_pits)) + str(board.north) + \
                    '-'.join(map(str, board.south_pits)) + str(board.south) + \
                    str(board.active_player)
        return board_str


    @staticmethod
    def display(board):
        print(str(board))   