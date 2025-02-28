#!/usr/bin/env python3

import KalahLogic as kgp
import math
import random
import time

def evaluate(state, side=kgp.SOUTH):
    return state[side] - state[not side]

def search(state, depth, side, alpha, beta, max_player_side=kgp.SOUTH):

    def child(move):
        
        if depth <= 0:
            return (evaluate(state, max_player_side), move)

        after, again = state.sow(side, move)
        if after.is_final():
            return (evaluate(after, max_player_side), move)
        if again:
            return (search(after, depth, side, alpha, beta)[0], move)
        else:
            return (search(after, depth-1, not side, alpha, beta)[0], move)

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

def minmax_move_arena(minmax_func, state, move_time, side, tree):
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


def minmax_agent(state, side = kgp.SOUTH, max_player_side=kgp.SOUTH):
    # print(state)
    for depth in range(1, 100):
        res = search(state, depth, side, -math.inf, math.inf, max_player_side)[1]
        
        yield res


# if __name__ == "__main__":
#     import os
#     kgp.connect(minmax_agent, 
#                 host="localhost", 
#                 port=2671, 
#                 debug=True, 
#                 token="BBBBB", 
#                 authors = ["Firevince"],
#                 name="Minmax ordered moves")
    


if __name__ == "__main__":
    board = kgp.Board.parse("<8,0,0,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8>")
    for move in minmax_agent(board, side=True):    
        print(move)


