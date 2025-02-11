from MCTS_agent_vince import MCTS, mcts_move_arena
from minimax_agent_vince import minmax_move_arena, minmax_agent

def hybrid_move(search_func, state, move_time, side, tree):
    '''simulates hybrid move
        first uses mcts then minmax
        returns new tree and new state'''
    myMCTS = MCTS(MCTS.Evaluation.BINARY, MCTS.Effort.RANDOM)

    if sum(state.north_pits) + sum(state.south_pits) < 20:
        return minmax_move_arena(minmax_agent, state, move_time, side, tree)
    else:
        return mcts_move_arena(myMCTS.search_monte_carl, state, move_time, side, tree)
