#!/usr/bin/env python3

# To write a Python client, we first need to import kgp.  In case
# "kgp.py" is not in the current working directory, adjust your
# PYTHONPATH.
import multiprocessing
multiprocessing.set_start_method("fork")

import kgp
import numpy as np
from kgp import Board

ETA = .8

def agent(state: Board):
    #(state, side, move) : new state
    calculated_states = {}
    
    #(state, side, move) : (score, next player)
    evaluated_moves = {}


    def evaluate_state(state: Board, eta=.8):
        assert 0 <= eta <= 1, 'Eta must be in [0,1]'
        player = eta * state.south + (1-eta) * sum(state.south_pits)
        opponent = eta * state.north + (1-eta) * sum(state.north_pits)
        return player - opponent


    def evaluate_move(state: Board, side, move):
        key = (str(state), side, move)
        # was evaluation already calculated
        if key in evaluated_moves:
            return evaluated_moves[key][0]

        score = 0
        next_player = not side

        # where will last seed land for given move
        seeds = state.pit(side, move)
        landing_pit = (move + seeds) % (state.size*2 + 1)

        # is there a extra move, then return high score
        # should result in placement in the beginning of sorted move list
        if landing_pit == state.size:
            score = 999
            next_player = side
        
        # can seeds be captured, then return capturing value as score
        elif landing_pit < state.size and state.pit(side, landing_pit) == 0:
            opposite_pit = state.size - 1 - landing_pit
            capture_value = state.pit(not side, opposite_pit) + 1
            score = capture_value

        evaluated_moves[key] = (score, next_player)
        return score
    

    def minimax(state: Board, side, depth, alpha=-np.inf, beta=np.inf):
        # base case
        legal_moves = state.legal_moves(side)
        if depth == 0 or not legal_moves:
            return None, evaluate_state(state, ETA)
        
        # evaluate all possible moves and sort them as: extra move, capture seeds, rest
        # determine the next player for every move on the way
        moves_with_scores = [(move, evaluate_move(state, side, move)) for move in legal_moves]
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
                    calculated_states[key] = state.sow(side, move)[0]

                # call minimax for next state and evaluate the result
                _, value = minimax(calculated_states[key], evaluated_moves[key][1], depth-1, alpha, beta)
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
                    calculated_states[key] = state.sow(side, move)[0]
                
                # call minimax for next state and evaluate the result
                _, value = minimax(calculated_states[key], evaluated_moves[key][1], depth-1, alpha, beta)
                if value < best_value:
                    best_value = value
                    best_move = move

                # alpha-beta-pruning
                beta = min(beta, best_value)
                if alpha >= beta:
                    return best_move, best_value

        return best_move, best_value


    for i in range(1, 15):
        yield minimax(state, kgp.SOUTH, i)[0]
        

#export SSL_CERT_FILE=$(python3 -m certifi)

if __name__ == "__main__":
    host = "wss://kalah.kwarc.info/socket" #if os.getenv("USE_WEBSOCKET") else "localhost"
    token = 'c+G6YUZAjTqEkQ==kdot'
    kgp.connect(agent, host=host, token=token, name='NotLikeUs')

    