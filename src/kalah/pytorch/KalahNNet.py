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


class ResidualBlock(nn.Module):
    def __init__(self, in_features):
        super(ResidualBlock, self).__init__()
        self.fc = nn.Linear(in_features, in_features)
        self.bn = nn.BatchNorm1d(in_features)

    def forward(self, x):
        residual = x
        out = F.relu(self.bn(self.fc(x)))
        out = self.bn(self.fc(out))
        out += residual
        return F.relu(out)

class KalahNNet_128res(nn.Module):
    def __init__(self, game, args):
        # game params
        self.board_x, self.board_y = game.getBoardSize()
        self.action_size = game.getActionSize()
        self.args = args

        super(KalahNNet_128res, self).__init__()
        self.fc1 = nn.Linear(self.board_x * self.board_y, 128)
        self.bn1 = nn.BatchNorm1d(128)

        # 3 Residual Blocks
        self.res1 = ResidualBlock(128)
        self.res2 = ResidualBlock(128)
        self.res3 = ResidualBlock(128)

        self.fc2 = nn.Linear(128, self.action_size)
        self.fc3 = nn.Linear(128, 1)

    def forward(self, s):
        #                                                           s: batch_size x board_x x board_y
        s = s.view(-1, self.board_x * self.board_y)                # batch_size x (board_x * board_y)
        s = F.relu(self.bn1(self.fc1(s)))                          # batch_size x 128

        s = self.res1(s)                                           # batch_size x 128
        s = self.res2(s)                                           # batch_size x 128
        s = self.res3(s)                                           # batch_size x 128

        pi = self.fc2(s)                                           # batch_size x action_size
        v = self.fc3(s)                                            # batch_size x 1

        return F.log_softmax(pi, dim=1), torch.tanh(v)
