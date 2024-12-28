import kgp
import math
import random


def evaluate(state):
    return state[kgp.SOUTH] - state[kgp.NORTH]

class searchtree:
    def __init__(self, state:kgp.Board, side=kgp.NORTH):
        self.wins = 0
        self.simuls = 0
        self.state = state
        self.side = side
        self.children = []

    def is_leave(self):
        return self.children == []



def search_monte_carlo(node, N):

    def expand_children(node):
        for move in node.state.legal_moves():
            after, again = state.sow(node.side, move)
            node.children.append(searchtree(after, not side))

    def get_best_ucb_child(node, c, N):
        ucbs = []
        for child in node.children: 
            if child.simuls == 0:       # the ucb would be infinity 
                ucbs = [(child, 1000)]
                break
            ucb = (child.wins/child.simuls) + c * math.sqrt(math.log(N)/child.simuls)
            ucbs.append((child, ucb))
        
        return max(ucbs, key = lambda x: x[1])[0]

    def traverse(node: searchtree, N, c=2):

        if node.is_leave():
            if node.simuls > 0:         
                node.children = expand_children(node)
            else:
                res = rollout(node.state, node.side)
                node.wins += res[0]
                node.simuls += 1
                return res
        
        bestchild = get_best_ucb_child(node, c, N)

        res = traverse(bestchild, N, c)

        node.wins += res[0] #backtracking
        node.simuls += 1
        return res

    def rollout(state, side):
        move = random.choice(state.legal_moves(side))
        after, again = state.sow(side, move)
        if after.is_final():
            return (evaluate(after), move)
        
        return rollout(after, not side)
    

    

    return traverse(node, N)

board = kgp.Board.parse("<8,0,2,9,9,9,9,8,8,8,8,0,9,9,0,10,10,10,10>")
tree = searchtree(board, kgp.NORTH)
search_monte_carlo(tree, 0)

    