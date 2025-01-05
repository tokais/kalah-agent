from MCTS import mcts_agent
from client import agent
import time
import kgp


# board = kgp.Board.parse("<8,0,0,8,0,8,8,8,8,8,8,7,8,8,8,8,8,8,8>")
board = kgp.Board.parse("<8,0,0,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8>")
end = time.time() + 10   


for best_move in mcts_agent(board):
    print(best_move)
    # if time.time() > end:
    #     break
    
