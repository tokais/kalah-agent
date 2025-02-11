import math
import random

class Node:
    def __init__(self, board, side, parent=None):
        self.board = board          # Current game state
        self.side = side            # Player to move (True: NORTH, False: SOUTH)
        self.parent = parent        # Parent node
        self.children = {}          # Maps moves to child nodes
        self.visits = 0             # Number of times node was visited
        self.total_reward = 0.0     # Accumulated reward from simulations
        self.possible_moves = board.legal_moves(side)  # Legal moves for current player
        self.is_terminal = len(self.possible_moves) == 0  # Terminal state check

    def select_child(self):
        """Select child with highest UCB1 score."""
        best_score = -float('inf')
        best_move = None
        best_child = None

        for move, child in self.children.items():
            if child.visits == 0:
                score = float('inf')
            else:
                exploitation = child.total_reward / child.visits
                exploration = math.sqrt(math.log(self.visits) / child.visits)
                score = exploitation + math.sqrt(2) * exploration  # UCB1 formula

            if score > best_score:
                best_score, best_move, best_child = score, move, child

        return best_move, best_child

    def expand(self):
        """Expand the node by adding a new child from an unexplored move."""
        for move in self.possible_moves:
            if move not in self.children:
                new_board, extra_move = self.board.sow(self.side, move)
                child_side = self.side if extra_move else not self.side
                child_node = Node(new_board, child_side, self)
                self.children[move] = child_node
                return child_node
        return None  # All moves expanded (shouldn't reach if not terminal)

    def update(self, outcome):
        """Backpropagate the simulation outcome and update node statistics."""
        if outcome == 0.5:
            reward = 0.5
        else:
            # Reward is 1 if the node's side matches the outcome, else 0
            reward = 1.0 if (self.side == (outcome == 1.0)) else 0.0

        self.visits += 1
        self.total_reward += reward

        if self.parent:
            self.parent.update(outcome)  # Recursively update parents

def monte_carlo_tree_search(root_board, root_side, iterations=1000):
    """Perform MCTS to find the best move for the current game state."""
    root_node = Node(root_board, root_side)

    for _ in range(iterations):
        node = root_node
        path = [node]

        # Selection phase: Traverse tree until a leaf node is found
        while True:
            if node.is_terminal:
                break
            if len(node.children) < len(node.possible_moves):
                break  # Node is expandable
            move, child = node.select_child()
            if child is None:
                break
            node = child
            path.append(node)

        # Expansion phase: Expand the node if not terminal
        if not node.is_terminal:
            child = node.expand()
            if child:
                path.append(child)
                node = child

        # Simulation phase: Play out the game until terminal state
        if node.is_terminal:
            # Determine outcome from current board state
            north_score = node.board.get_store(True)
            south_score = node.board.get_store(False)
            if north_score > south_score:
                outcome = 1.0
            elif south_score > north_score:
                outcome = 0.0
            else:
                outcome = 0.5
        else:
            # Random playout from the current state
            current_board = node.board
            current_side = node.side
            while True:
                possible_moves = current_board.legal_moves(current_side)
                if not possible_moves:
                    # Game over, calculate final scores
                    north_score = current_board.get_store(True)
                    south_score = current_board.get_store(False)
                    if north_score > south_score:
                        outcome = 1.0
                    elif south_score > north_score:
                        outcome = 0.0
                    else:
                        outcome = 0.5
                    break
                # Choose random move and update state
                move = random.choice(possible_moves)
                new_board, extra_move = current_board.sow(current_side, move)
                current_board = new_board
                current_side = current_side if extra_move else not current_side

        # Backpropagation phase: Update nodes with the outcome
        for node in reversed(path):
            node.update(outcome)

    # Choose the move with the highest visit count
    best_move = max(root_node.children.keys(), key=lambda m: root_node.children[m].visits)
    return best_move