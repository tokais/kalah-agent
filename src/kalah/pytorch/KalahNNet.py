import sys
sys.path.append('..')
from src.utils import *

import argparse
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

class KalahNNet(nn.Module):
    def __init__(self, game, args):
        # game params
        self.board_x, self.board_y = game.getBoardSize()
        self.action_size = game.getActionSize()
        self.args = args

        super(KalahNNet, self).__init__()
        self.fc1 = nn.Linear(self.board_x * self.board_y, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, self.action_size)
        self.fc4 = nn.Linear(64, 1)


    def forward(self, s):
        #                                                           s: batch_size x board_x x board_y
        s = s.view(-1, self.board_x * self.board_y)                # batch_size x 1 x (board_x * 2)
        s = F.relu(self.fc1(s))                          # batch_size x num_channels x board_x x board_y
        s = F.relu(self.fc2(s))                          # batch_size x num_channels x board_x x board_y
       
        pi = self.fc3(s)                                                                         # batch_size x action_size
        v = self.fc4(s)                                                                          # batch_size x 1

        return F.log_softmax(pi, dim=1), torch.tanh(v)
