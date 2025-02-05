import kgp
import math
import random
import sys
import time
import copy
from MCTS import searchtree, search_monte_carl, evaluate

from mm_client import minmax_agent


BOARD = kgp.Board.parse("<8,0,0,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8>")
# BOARD = kgp.Board.parse("<8,5,7,15,15,3,16,4,1,4,6,14,4,3,2,3,0,9,17>")
# BOARD = kgp.Board.parse("<8,64,49,0,3,2,1,1,2,0,1,0,0,0,0,0,3,1,1>")


def player_move(tree):
    new_tree = copy.deepcopy(tree)
    mymove = None
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
                new_tree.simuls = 1
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
        exit(1)
    return new_tree


def mcts_move(state:kgp.Board, move_time:int, side, tree:searchtree):
    tree = tree.find_node(state)
    if tree is None:
        print("started new tree")
        tree = searchtree(state, side)
        tree.simuls = 1
    N = tree.simuls
    new_tree = copy.deepcopy(tree)
    again = True
    while again:
        best_move = 0
        end = time.time() + move_time  
        while time.time() < end:
            new_tree, N, new_best_move = search_monte_carl(new_tree, N, side)
            if new_best_move != best_move:
                best_move = new_best_move
                print(best_move, end=" ")
                # print(new_tree.state)
                # print(best_move)
        # print(f"calculated {N} moves")
        new_tree=new_tree.children[best_move]
        # print(new_tree.state)
        if new_tree.state.is_final():
            again = False
        elif new_tree.side != side:
            again = False
        else:
            print("Calculating another move ...")

    return new_tree, new_tree.state

def minmax_move(state, move_time, side, tree):
    best_move = -1
    end = time.time() + move_time  
    again = True
    while again:
        again = False
        for move in minmax_agent(state, side):
            if time.time() > end:
                break
            print(best_move, end=",")
            if move != best_move:
                best_move = move
                new_state, again = tree.state.sow(side, best_move)
        if again:
            print("Calculating another move ...")
    return tree, new_state



def hybrid_move(state, move_time, side, tree):
    if sum(state.north_pits) + sum(state.south_pits) < 20:
        return minmax_move(state, move_time, side, tree)
    else:
        return mcts_move(state, move_time, side, tree)

def play_interactive():
    tree = searchtree(BOARD, kgp.SOUTH)
    tree.simuls = 1
    time = 3

    while True:
        print(tree.state)
        tree, state = mcts_move(tree.state, time, kgp.NORTH, tree)
        if state.is_final():
            print("Game ended")
            print(("South won" if state[kgp.SOUTH] - state[kgp.NORTH] > 0 else "North won"))
            break
        tree = player_move(tree)
        if state.is_final():
            print("Game ended")
            print(("South won" if state[kgp.SOUTH] - state[kgp.NORTH] > 0 else "North won"))
            break

def bot_make_move(play_func, name, state, time, side, tree):
    tree, state = play_func(state, time, side, tree)
    print(f"{name}: ")
    print(state)
    return tree, state

def arena():
    tree = searchtree(BOARD, kgp.SOUTH)
    state = BOARD
    tree.simuls = 1
    time = 3
    north = 0
    south = 0
    res = 0
    
    north_player = "hybrid"
    north_player_func = hybrid_move
    south_player = "minmax"
    south_player_func = minmax_move

    print(f"Arena: {north_player} (South) vs. {south_player} (Nort)")
    for i in range(100):
        with open("arena.txt", "a") as f:
            f.write(f"Game {i}\n")
            f.write(f"{north_player}(North): {north}, {south_player}(South): {south}, Result: {res}\n")
            
        tree = searchtree(BOARD, kgp.SOUTH)
        state = BOARD
        tree.simuls = 1
        while True:
            tree, state = bot_make_move(north_player_func, north_player, state, time, kgp.NORTH, tree)
            if state.is_final():
                break
            tree, state = bot_make_move(south_player_func, south_player, state, time, kgp.SOUTH, tree)
            if state.is_final():
                break
        
        res += (1 if (state[kgp.SOUTH] - state[kgp.NORTH]) > 0 else 0)
        north += state[kgp.NORTH]
        south += state[kgp.SOUTH]

if __name__ == "__main__":
    arena()
    if sys.argv[1] == "interactive":
        play_interactive()  
    elif sys.argv[1] == "arena":
        arena()