#!/usr/bin/env python3

import kgp
import math
import random
from MCTS import mcts_agent

def evaluate(state):
    return state[kgp.SOUTH] - state[kgp.NORTH]


def search(state, depth, side, alpha, beta):

    def child(move):
        
        if depth <= 0:
            return (evaluate(state), move)

        after, again = state.sow(side, move)
        if after.is_final():
            return (evaluate(after), move)
        if again:
            return (search(after, depth, side, alpha, beta)[0], move)
        else:
            return (search(after, depth-1, not side, alpha, beta)[0], move)

    childs = []
    for move in state.legal_moves(side):
        ev, move = child(move) 
        childs.append((ev, move))

        if side == kgp.SOUTH:   
            alpha = max(alpha, ev)
            if beta <= alpha:
                break
        else:
            beta = min(beta, ev)
            if beta <= alpha:
                break
        
    choose = max if side == kgp.SOUTH else min

    return choose(childs, key=lambda ent: ent[0])


def agent(state):
    print(state)
    for depth in range(1, 100):
        res = search(state, depth, kgp.SOUTH, -math.inf, math.inf)[1]
        
        yield res


if __name__ == "__main__":
    import os
    kgp.connect(agent, 
                host="localhost", 
                port=2671, 
                debug=True, 
                token="BBBBB", 
                authors = ["Firevince"],
                name="Minmax Mein Freund")
    # kgp.connect(agent, host    = "wss://kalah.kwarc.info/socket",
    #                    token   = "CCCCCCCCC",
    #                    debug   = True,
    #                    authors = ["Firevince"],
    #                    name    = "FireFire")


