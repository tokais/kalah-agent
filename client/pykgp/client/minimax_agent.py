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
            return None, evaluate_state(state, ETA)
        
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
                    calculated_states[key] = state.sow(side, move)[0]

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
                    calculated_states[key] = state.sow(side, move)[0]
                
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
        

#export SSL_CERT_FILE=$(python3 -m certifi)

if __name__ == "__main__":
    host = "wss://kalah.kwarc.info/socket" #if os.getenv("USE_WEBSOCKET") else "localhost"
    #token = 'c+G6YUZAjTqEkQ==kdot'
    token = 'c+G6YUZAjTqEkQ==kdot2'
    kgp.connect(agent, host=host, token=token, name='EvenLessThanUs')

    