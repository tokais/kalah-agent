import kgp
import sys
import time
import copy
from client.scripts.MCTS_agent_vince import searchtree, MCTS, mcts_move_arena

from client.scripts.minimax_agent_vince import minmax_agent, minmax_move_arena
from hybrid_agent import hybrid_move

BOARD = kgp.Board.parse("<8,0,0,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8>")


# BOARD = kgp.Board.parse("<4,0,0,8,8,8,8,8,8,8,8>")
# BOARD = kgp.Board.parse("<8,5,7,15,15,3,16,4,1,4,6,14,4,3,2,3,0,9,17>")
# BOARD = kgp.Board.parse("<8,64,49,0,3,2,1,1,2,0,1,0,0,0,0,0,3,1,1>")



def player_move(tree, side):
    '''simulates player move
        returns new tree and new state'''
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
        if mymove < 0 or mymove >= new_tree.state.size or not new_tree.state.is_legal(side, mymove):
            mymove = None
            print("not a legal move")
            continue
        
        state, again = new_tree.state.sow(side, mymove)
        for i in range(int(mymove)):
            if not new_tree.state.is_legal(side, i):
                mymove -= 1

        if again:
            if new_tree.children == []:
                print("started new tree")
                new_tree = searchtree(state, not side)
                new_tree.simuls = 1
            else:
                new_tree = new_tree.children[int(mymove)]
            mymove = None
            print("you have another turn")
            print(new_tree.state)
    
    if new_tree.children == []:
        print("started new tree")
        new_tree = searchtree(state, not side)
        new_tree.simuls = 1
    else:
        new_tree = new_tree.children[int(mymove)]
    
    if new_tree.state:
        print(new_tree.state)
    elif new_tree.state.is_final():
        input("Game ended")
        exit(1)
    return new_tree, new_tree.state


def play_interactive():
    '''simulates interactive game between player and bot'''
    tree = searchtree(BOARD, kgp.SOUTH)
    tree.simuls = 1
    time = 3

    myMCTS = MCTS(MCTS.Evaluation.BINARY, MCTS.Effort.RANDOM)


    while True:
        print(tree.state)
        tree, state = player_move(tree, kgp.SOUTH)
        if state.is_final():
            print("Game ended")
            print(("South won" if state[kgp.SOUTH] - state[kgp.NORTH] > 0 else "North won"))
            break
        tree, state = mcts_move_arena(myMCTS.search_monte_carl, tree.state, time, kgp.NORTH, tree)
        if state.is_final():
            print("Game ended")
            print(("South won" if state[kgp.SOUTH] - state[kgp.NORTH] > 0 else "North won"))
            break
        



def bot_make_move(play_func, search_func, name, state, time, side, tree):
    '''wrapper for bot move functions'''
    tree, state = play_func(search_func, state, time, side, tree)
    print(f"{name}: ")
    print(state)
    return tree, state

def arena():
    '''simulates 100 games between two bot agents'''
    tree = searchtree(BOARD, kgp.SOUTH)
    state = BOARD
    tree.simuls = 1
    time = 3
    north = 0
    south = 0
    res = 0
    
    # north_player = "hybrid"
    # north_player_search_func = hybrid_move
    # north_player_play_func = hybrid_move

    myMCTS = MCTS(MCTS.Evaluation.BINARY, MCTS.Effort.GREEDY)
    north_player = "mcts_greedy"
    north_player_search_func = myMCTS.search_monte_carl
    north_player_play_func = mcts_move_arena

    south_player = "minmax"
    south_player_search_func = minmax_agent
    south_player_play_func = minmax_move_arena

    print(f"Arena: {north_player} (South) vs. {south_player} (Nort)")
    for i in range(100):
        with open("arena.txt", "a") as f:
            f.write(f"Game {i}\n")
            f.write(f"{north_player}(North): {north}, {south_player}(South): {south}, Result: {res}\n")
            
        tree = searchtree(BOARD, kgp.SOUTH)
        state = BOARD
        tree.simuls = 1
        while True:
            tree, state = bot_make_move(north_player_play_func, north_player_search_func, north_player, state, time, kgp.NORTH, tree)
            if state.is_final():
                break
            tree, state = bot_make_move(south_player_play_func, south_player_search_func, south_player, state, time, kgp.SOUTH, tree)
            if state.is_final():
                break
        
        res += (1 if (state[kgp.SOUTH] - state[kgp.NORTH]) > 0 else 0)
        north += state[kgp.NORTH]
        south += state[kgp.SOUTH]


if __name__ == "__main__":
    # arena()
    if sys.argv[1] == "interactive":
        play_interactive()  
    elif sys.argv[1] == "arena":
        arena()