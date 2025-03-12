import math
import random
import time

import numpy as np

import src.kalah.kgp as kgp
from src.kalah.KalahGame import KalahGame
from src.kalah.KalahLogic import Board
from src.kalah.pytorch.KalahNNet import KalahNNet_128res
from src.kalah.pytorch.NNetWrapper import NNetWrapper
from src.MCTS import MCTS
from src.utils import dotdict

"""
Random and Human-ineracting players for the game of TicTacToe.

Author: Evgeny Tyurin, github.com/evg-tyurin
Date: Jan 5, 2018.

Based on the OthelloPlayers by Surag Nair.

"""
class RandomPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board):
        a = np.random.randint(self.game.getActionSize())
        valids = self.game.getValidMoves(board, 1)
        while valids[a]!=1:
            a = np.random.randint(self.game.getActionSize())
        return a

class minmax_vince_player:
    def evaluate(state, side=kgp.SOUTH):
        return state[side] - state[not side]

    def search(self, state:Board, depth, side, alpha, beta, max_player_side=kgp.SOUTH):

        def child(move):
            
            if depth <= 0:
                return (self.evaluate(state, max_player_side), move)

            after, again = state.execute_move(side, move)
            if after.is_final():
                return (self.evaluate(after, max_player_side), move)
            if again:
                return (self.search(after, depth, side, alpha, beta)[0], move)
            else:
                return (self.search(after, depth-1, not side, alpha, beta)[0], move)

        childs = []
        ordered_moves = sorted(state.legal_moves(side), key=lambda move: -state[side, move])
        for move in ordered_moves:
            ev, move = child(move) 
            childs.append((ev, move))

            if side == max_player_side:   
                alpha = max(alpha, ev)
                if beta <= alpha:
                    break
            else:
                beta = min(beta, ev)
                if beta <= alpha:
                    break
            
        choose = max if side == max_player_side else min

        return choose(childs, key=lambda ent: ent[0])

    def minmax_move_arena(self, minmax_func, state, move_time, side, tree):
        '''simulates minmax move
            returns new tree and new state'''
        best_move = -1
        end = time.time() + move_time  
        again = True
        while again:
            again = False
            for move in minmax_func(state, side):
                if time.time() > end:
                    break
                print(best_move, end=",")
                if move != best_move:
                    best_move = move
                    new_state, again = tree.state.sow(side, best_move)
            if again:
                print("Calculating another move ...")
        return tree, new_state


    def minmax_agent(self, state, side = kgp.SOUTH, max_player_side=kgp.SOUTH):
        # print(state)
        for depth in range(1, 100):
            res = self.search(state, depth, side, -math.inf, math.inf, max_player_side)[1]
            
            yield res


class minmax_tobi_player:
    def __init__(self):
        self.ETA = 0.8

    def agent(self,state: Board):
        #(str(state), side, move) : new state
        calculated_states = {}
        
        #(str(state), side, move) : (score, next player)
        evaluated_moves = {}

        #(str(state), side, depth) : move
        prev_best_move = {}

        def evaluate_state(state: Board, eta=.8):
            assert 0 <= eta <= 1, 'Eta must be in [0,1]'
            south = eta * state.south + (1-eta) * sum(state.south_pits)
            north = eta * state.north + (1-eta) * sum(state.north_pits)
            return south - north


        def evaluate_move(state: Board, side, move, depth):
            evaluation_key = (str(state), side, move)
            # was evaluation already calculated
            if evaluation_key in evaluated_moves:
                return evaluated_moves[evaluation_key][0]

            score = 0
            next_player = not side

            # where will last seed land for given move
            seeds = state.pit(side, move)
            landing_pit = (move + seeds) % (state.size*2 + 1)

            # best move already found in previos iteration, then search it first
            best_move_key = (str(state), side, depth)
            if best_move_key in prev_best_move and prev_best_move[best_move_key] == move:
                score = 1000
                if landing_pit == state.size:
                    next_player = side

            # is there a extra move, then search it second
            # should result in placement in the beginning of sorted move list
            elif landing_pit == state.size:
                score = 999
                next_player = side
            
            # can seeds be captured, then return capturing value as score
            elif landing_pit < state.size and state.pit(side, landing_pit) == 0:
                opposite_pit = state.size - 1 - landing_pit
                capture_value = state.pit(not side, opposite_pit) + 1
                score = capture_value

            evaluated_moves[evaluation_key] = (score, next_player)
            return score
        

        def minimax(state: Board, side, max_depth, depth=0, alpha=-np.inf, beta=np.inf):
            # base case: reached desired depth or no more moves possible
            legal_moves = state.legal_moves(side)
            if depth == max_depth or not legal_moves:
                return None, evaluate_state(state, self.ETA)
            
            # evaluate all possible moves and sort them as: best move in previous iteration, extra move, capture seeds, rest
            # determine the next player for every move on the way
            moves_with_scores = [(move, evaluate_move(state, side, move, depth)) for move in legal_moves]
            moves_with_scores.sort(key=lambda x: -x[1])
            moves = [move for move, _ in moves_with_scores]

            best_move = best_value = None

            # south's turn (maximizing player)
            if side == kgp.SOUTH:
                best_value = -np.inf
                for move in moves:
                    # calculate next state
                    key = (str(state), side, move)
                    if key not in calculated_states:
                        calculated_states[key] = state.execute_move(side, move)[0]

                    # call minimax for next state and evaluate the result
                    _, value = minimax(calculated_states[key], evaluated_moves[key][1], max_depth, depth+1, alpha, beta)
                    if value > best_value:
                        best_value = value
                        best_move = move
                    
                    # alpha-beta-pruning
                    alpha = max(alpha, best_value)
                    if alpha >= beta:
                        return best_move, best_value

            # north's turn (minimizing player)
            else:
                best_value = np.inf
                for move in moves:
                    # calculate next state
                    key = (str(state), side, move)
                    if key not in calculated_states:
                        calculated_states[key] = state.execute_move(side, move)[0]
                    
                    # call minimax for next state and evaluate the result
                    _, value = minimax(calculated_states[key], evaluated_moves[key][1], max_depth, depth+1, alpha, beta)
                    if value < best_value:
                        best_value = value
                        best_move = move

                    # alpha-beta-pruning
                    beta = min(beta, best_value)
                    if alpha >= beta:
                        return best_move, best_value

            # store best move to speed up following iterations
            key = (str(state), side, depth)
            prev_best_move[key] = best_move

            return best_move, best_value

        # iterative deepening
        for i in range(1, 20):
            yield minimax(state, kgp.SOUTH, i)[0]
            
class human_player:
    def __call__(self, board:Board):
        '''simulates player move
            returns new tree and new state'''
        mymove = None
        side = True
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
    
    # def notify(self, board:Board, action):
    #     print(f"Opponent chose: {action+1}")

class time_control:
    def __init__(self, move_time = 3):
        self.move_time = move_time
               
    def __call__(self, board:Board):
        '''dont need to rerun bc arena handles again moves'''
        verbos = False
        best_move = -1
        end = time.time() + self.move_time  

        # for move in minmax_agent(board, side=NORTH, max_player_side=NORTH):
        for move in minmax_tobi_player().agent(board):
            if time.time() > end:
                break
            if verbos:
                print(best_move, end=",")
            if move != best_move:
                best_move = move
        return best_move


class alpha_zero_player:
    args = dotdict({          
        'numMCTSSims': 50,          # Number of games moves for MCTS to simulate.
        'cpuct': 1,
    })

    def __init__(self, 
                 filename='best.pth.tar', 
                 folder='best_models',
                 mcts= None,
                 depth_list:list=[1000], 
                 online_phase=False,
                 verbose=False
                 ):
        self.filename = filename
        self.online_phase = online_phase
        self.depth_list = depth_list
        self.verbose=verbose
        g = KalahGame()

        if mcts is None:
            nnet = NNetWrapper(KalahNNet_128res, g)
            nnet.load_checkpoint(folder=folder, filename=self.filename)
            self.nmcts = MCTS(g, nnet, self.args)
        else:
            self.nmcts = mcts
        
    def __call__(self, board:Board):
        return self.get_move(board).__next__()

    def get_move(self, board:Board):
        if self.online_phase:
            board.active_player = -1
        best_move = -1

        if self.verbose:
            print(board)

        for depth in self.depth_list:
            pi = self.nmcts.getInstantActionProb(board, depth, temp=0)
            if self.online_phase:
                move = np.argmax(pi)
            else:
                move = np.random.choice(len(pi), p=pi)
            
            if move != best_move:
                best_move = move
                if self.verbose:
                    print(best_move, end=",")
                    print(board.sow((board.active_player+1)//2, best_move)[0])

            yield move

    # def notify(self, board:Board, action):
    #     print(f"Opponent chose: {action+1}")
    #     KalahGame().display(board)




if __name__ == "__main__":
    host = "wss://kalah.kwarc.info/socket" #if os.getenv("USE_WEBSOCKET") else "localhost"
    token = 'c+G6YUZAjTqEkQ==kdot2'
    kgp.connect(minmax_tobi_player().agent, 
                host=host, 
                token=token, 
                name='EvenLessThanUs', 
                debug=True)

    