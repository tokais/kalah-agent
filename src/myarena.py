import multiprocessing
import time

import numpy as np

from kalah.KalahGame import KalahGame
from kalah.KalahLogic import Board, connect
# import kalah.kgp as kgp
from kalah.KalahPlayers import (alpha_zero_player, minmax_tobi_player,
                                minmax_vince_player)
from kalah.pytorch.KalahNNet import KalahNNet, KalahNNet_128res
from src.Arena import Arena
from src.kalah.pytorch.NNetWrapper import NNetWrapper
from src.MCTS import MCTS
from src.utils import *

multiprocessing.set_start_method("fork")


NORTH = True
SOUTH = not NORTH

BOARD = Board.parse("<8,0,0,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8>")





def main():
    g = KalahGame()
    depth_list = [200]
    arena = Arena(player1=alpha_zero_player(filename='best_128res_3.pth.tar', depth_list=depth_list), 
                player2=alpha_zero_player(filename='best_128res_2.pth.tar', depth_list=depth_list),
                game=g,
                display=g.display)
    start = time.time()
    player_one_wins, player_two_wins, draws = arena.playGames(8, verbose=False)
    print("Time elapsed:", time.time() - start)
    print("one_wins", player_one_wins)
    print("two_wins", player_two_wins)
    print("draws", draws)


if __name__ == "__main__": 
    # with multiprocessing.Manager() as manager:
    #     calculated_states = manager.dict()

    main()


# if __name__ == "__main__":
#     with multiprocessing.Manager() as manager:
#         calculated_states = manager.dict()
#         host = "wss://kalah.kwarc.info/socket" #if os.getenv("USE_WEBSOCKET") else "localhost"
#         token = 'c+G6YUZAjTqEkQ=='
#         connect(alpha_zero_move(filename='best_128res.pth.tar', online_phase=True).get_move, 
#                 host    = "wss://kalah.kwarc.info/socket",
#                 token   = "CCCCCCCCC",
#                 debug   = True,
#                 authors = ["Firevince"],
#                 name    = "alpha_dude")

# if __name__ == "__main__":
#     with multiprocessing.Manager() as manager:
#         calculated_states = manager.dict()
#         host = "wss://kalah.kwarc.info/socket" #if os.getenv("USE_WEBSOCKET") else "localhost"
#         token = 'Miaumiau'
#         connect(alpha_zero_move(filename='best_128res.pth.tar').get_move, host=host, token=token, name='alphadude', debug=True)
