import multiprocessing
multiprocessing.set_start_method("fork")

import kgp
import numpy as np
from kgp import Board
import random


#(state, side, move) : new state
calculated_states = {}


def evaluateState(state: Board):
    return state.south - state.north


class Node:
    def __init__(self, state: Board, side, parent=None):
        self.state = state
        self.side = side
        self.parent = parent
        self.children = []
        self.visits = 0.
        self.wins = 0.

    def is_fully_expanded(self):
        return len(self.children) == len(self.state.legal_moves(self.side))
    
    def best_child(self):
        return max(
            self.children,
            key=lambda child: child.wins / child.visits
        )
    

def selection(node: Node):
    while node.children and node.is_fully_expanded():
        node = node.best_child()
    return node


def expansion(node: Node):
    legal_moves = node.state.legal_moves(node.side)
    existing_moves = [child.state for child in node.children]
    for move in legal_moves:
        key = (str(node.state), node.side, move)
        if key not in calculated_states:
            new_state, _ = node.state.sow(node.side, move)
            calculated_states[key] = new_state
        else:
            new_state = calculated_states[key]
        if new_state not in existing_moves:
            child_node = Node(new_state, not node.side, node)
            node.children.append(child_node)
            return child_node
    return node


def evaluation(node: Node):
    current_state = node.state.copy()
    current_side = node.side
    while not current_state.is_final():
        legal_moves = current_state.legal_moves(current_side)
        if not legal_moves:
            break
        move = random.choice(legal_moves)
        key = (str(current_state), current_side, move)
        if key not in calculated_states:
            current_state, _ = current_state.sow(current_side, move)
            calculated_states[key] = current_state
        else:
            current_state = calculated_states[key]
        current_side = not current_side
    return evaluateState(current_state)


def backpropagation(node: Node, reward):
    while node is not None:
        node.visits += 1
        node.wins += reward
        reward = -reward
        node = node.parent


def mcts(state: Board, side, iterations):
    root = Node(state, side)
    for _ in range(iterations):
        leaf = selection(root)
        child = expansion(leaf)
        reward = evaluation(child)
        backpropagation(child, reward)
    best_child = root.best_child()
    for move in state.legal_moves(side):
        key = (str(state), side, move)
        if key not in calculated_states:
            child_state, _ = state.sow(side, move)
            calculated_states[key] = child_state
        else:
            child_state = calculated_states[key]
        if child_state == best_child.state:
            return move, best_child


def agent(state: Board):
    for i in [10, 20, 30, 40, 50]:
        yield mcts(state, kgp.SOUTH, i)[0]


if __name__ == "__main__":
    host = "wss://kalah.kwarc.info/socket" #if os.getenv("USE_WEBSOCKET") else "localhost"
    token = 'c+G6YUZAjTqEkQ==mcts'
    kgp.connect(agent, host=host, token=token, name='pineapplethemctsdude')