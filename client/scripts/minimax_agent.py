#!/usr/bin/env python3

# To write a Python client, we first need to import kgp.  In case
# "kgp.py" is not in the current working directory, adjust your
# PYTHONPATH.
import multiprocessing
multiprocessing.set_start_method("fork")

import kgp
import numpy as np
from kgp import Board

#(state, side, move) : new state
calculated_states = None

def evaluateState(state: Board):
    return state.south - state.north

def lastSeedToKalah(state: Board, side, move):
    key = (str(state), side, move)
    if key not in calculated_states:
        calculated_states[key] = state.sow(side, move)[0]
    if calculated_states[key][side] == state[side]+1:
        return True
    return False
        
#def lastSeedToPit(state: Board, side, move):
#    if state.pit(side, move) > 0 or state.pit(not side, move) == 0:
#        return False
#    for i in range(move+1, state.size):
#        if state.is_legal(side, i) is False:
#            continue
#        key = (str(state), side, i)
#        if key not in calculated_states:
#            calculated_states[key] = state.sow(side, i)[0]
#        if calculated_states[key][side] > state[side]+1:
#            return True
#    return False
    
def minimax(state: Board, side, depth, alpha=-np.inf, beta=np.inf):
    moves = state.legal_moves(side)
    if depth == 0 or not moves:
        return None, evaluateState(state)
    best_move = best_value = None
    if side == kgp.SOUTH:
        best_value = -np.inf
        for i in moves:
            key = (str(state), side, i)
            if key not in calculated_states:
                calculated_states[key] = state.sow(side, i)[0]
            _, value = minimax(calculated_states[key], not side, depth - 1, alpha, beta)
            if value > best_value:
                if lastSeedToKalah(state, side, i):
                    best_value = value + 2
                else:
                    best_value = value
                best_move = i
            alpha = max(alpha, best_value)
            if beta is not None and alpha >= beta:
                return best_move, best_value
    else:
        best_value = np.inf
        for i in moves:
            key = (str(state), side, i)
            if key not in calculated_states:
                calculated_states[key] = state.sow(side, i)[0]
            _, value = minimax(calculated_states[key], not side, depth - 1, alpha, beta)
            if value < best_value:
                if lastSeedToKalah(state, side, i):
                    best_value = value - 2
                else:
                    best_value = value
                best_move = i
            beta = min(beta, best_value)
            if alpha is not None and alpha >= beta:
                return best_move, best_value
    return best_move, best_value

def agent(state: Board):
    for i in range(1, 11):
        yield minimax(state, kgp.SOUTH, i)[0]
        
# We can now use the generator function as an agent.  The below
# configuration will check environmental variables that you can set to
# modify the behaviour of this agent.  The relevant options are:
#
# - USE_WEBSOCKET: Connect to the public practice server instead of
#   localhost.  You can set this for the duration of your session, to
#   always connect to the server
#
#   $ USE_WEBSOCKET=t export USE_WEBSOCKET
# 
#   By default the client will connect to your localhost on port 2761.
#   Keep in mind that this is the intended behaviour of your final
#   submission.  
#
#   Note that by default kgp.py requires that the "websocket-client"
#   library (not to be confused with "websockets", that ends with an
#   "s") has to be installed for Python 3, as the public server is only
#   accessible over a websocket connection.
#
# - TOKEN: A random string used to identify your agent.  Think of it
#   as password and username in one.  You can generate a satisfyingly
#   random token in a shell session by running the following command:
# 
#   $ tr -cd 'a-z' </dev/urandom | head -c100
#
# - NAME: Any name for your agent.  This is mainly to make identifying
#   it on the website it easier for you.  The name is public and can
#   be changed whenever the agent connects with the same token.
#
# As with everything here (including the library file kgp.py), you are
# free to change anything.  A more extensive, manual example includes
# some more agent metadata:
#
#     kgp.connect(agent, host    = "wss://kalah.kwarc.info/socket",
#                        token   = "A hopefully random string only I know",
#                        authors = ["Eva Lu Ator", "Ben Bitdiddle"],
#                        name    = "magenta")
#
# This will be sent to the server and used to identify a client over
# multiple connections.  You may leave out the TOKEN keyword, if you
# wish to stay anonymous, in which case your client will not appear on
# the website.

#export SSL_CERT_FILE=$(python3 -m certifi)

if __name__ == "__main__":
    with multiprocessing.Manager() as manager:
        calculated_states = manager.dict()
        host = "wss://kalah.kwarc.info/socket" #if os.getenv("USE_WEBSOCKET") else "localhost"
        token = 'c+G6YUZAjTqEkQ=='
        kgp.connect(agent, host=host, token=token, name='pineapplethefruitdude')

    
