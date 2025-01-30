import kgp
import math
import random
import sys
import time
import copy
from MCTS import searchtree, search_monte_carl

def player_move(tree):
    new_tree = copy.deepcopy(tree)
    mymove = None
    while mymove == None :
        try:
            mymove = input("Choose your move: ")
            mymove = int(mymove) - 1
        except:
            mymove = None
            print("not a number")
            continue
        if mymove < 0 or mymove >= new_tree.state.size or not new_tree.state.is_legal(kgp.NORTH, mymove):
            mymove = None
            print("not a legal move")
            continue
        
        state, again = new_tree.state.sow(kgp.NORTH, mymove)
        for i in range(int(mymove)):
            if not new_tree.state.is_legal(kgp.NORTH, i):
                mymove -= 1

        if again:
            if new_tree.children == []:
                print("started new tree")
                new_tree = searchtree(state, kgp.SOUTH)
            else:
                new_tree = new_tree.children[int(mymove)]
            mymove = None
            print("you have another turn")
            print(new_tree.state)
     
    new_tree = new_tree.children[int(mymove)]
    if new_tree.state:
        print(new_tree.state)
    elif new_tree.state.is_final():
        input("Game ended")
    return new_tree


def mcts_move(tree, N):
    new_tree = copy.deepcopy(tree)
    again = True
    while again:
        best_move = 0
        end = time.time() + 3   
        while time.time() < end:
            new_tree, N, new_best_move = search_monte_carl(new_tree, N, kgp.SOUTH)
            if new_best_move != best_move:
                best_move = new_best_move
                # print(new_tree.state)
                # print(best_move)
        # print(f"calculated {N} moves")
        new_tree=new_tree.children[best_move]
        # print(new_tree.state)
        if new_tree.side == kgp.NORTH:
            again = False
        # else:
        #     print("Calculating another move ...")

    return new_tree

def play_interactive():
    board = kgp.Board.parse("<8,0,0,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8>")
    tree = searchtree(board, kgp.SOUTH)
    tree.simuls = 1
    N = 1

    while True:
        tree = mcts_move(tree, N)
        tree = player_move(tree)


def arena():

    while True:
        tree = mcts_move(tree, 1)
        tree = player_move(tree)







if __name__ == "__main__":
    play_interactive()