import kgp
import math
import random
import sys
import time


def evaluate(state):
    return state[kgp.SOUTH] - state[kgp.NORTH]

class searchtree:
    def __init__(self, state:kgp.Board, side=kgp.SOUTH):
        self.wins = 0
        self.simuls = 0
        self.state = state
        self.side = side
        self.children = []

    def is_leave(self):
        return self.children == []

    def print_nodes(self, depth=0):
        print(self.state)
        print(f"D: {depth}, S: {self.simuls}, W: {self.wins}")
        if self.is_leave():
            return 
        for child in self.children:
            print(f"S: {child.simuls}, W: {child.wins}")
        best = max(self.children, key=lambda x: x.wins)
        best.print_nodes(depth +1)





def search_monte_carlo(node, N, best_move = 0):

    def expand_children(node):
        ''' If leave node would be explored a second time it 
            expands every next move into a child
            returns: children:[searchtree]'''

        children = []
        for move in node.state.legal_moves(node.side):
            after, again = node.state.sow(node.side, move)
            if again:
                children.append(searchtree(after, node.side))
            else:
                children.append(searchtree(after, not node.side))
        return children


    def get_best_ucb_child(node, side, N, c):
        ''' selects child with best upper confident bound - 
            balances between exploration and exploitation
            returns: child: searchtree'''
        

        ucbs = []
        for child in node.children: 
            if child.simuls == 0:       # the ucb would be infinity 
                ucbs = [(child, 1000)]
                break
            score = child.wins if side else child.simuls - child.wins # unsure
            ucb = (score/child.simuls) + c * math.sqrt(math.log(N)/child.simuls)
            ucbs.append((child, ucb))

        return max(ucbs, key=lambda ent: ent[1])[0]


    def traverse(node: searchtree, side:bool, N, c=2):
        '''traverses the known tree until it finds a child node
            returns: (evaluation: int, node: searchtree, simulations: int)'''

        if node.is_leave():
            if node.simuls > 0:   
                if node.state.is_final():
                      return (1 if evaluate(node.state) > 0 else 0), node, N  
                node.children = expand_children(node)
            else:
                res = rollout(node.state, node.side)
                node.wins += res
                node.simuls += 1
                return res, node, N
        

        bestchild = get_best_ucb_child(node, side, N, c)

        res, _, N = traverse(bestchild, not side, N + 1, c)

        node.wins += res #backtracking
        node.simuls += 1
        return res, node, N


    def rollout(state, side, depth = 0):
        '''full rollout - play a leave state with random play till end
            returns: evaluation:int'''
        if state.is_final():
            return (1 if evaluate(state) > 0 else 0)    # not sure which eval is better 
        
        move = random.choice(state.legal_moves(side))
        after, again = state.sow(side, move)

        try:
            if again:
                return rollout(after, side, depth + 1)   
            else:
                return rollout(after, not side, depth + 1)
        except:
            print("lol")
            return 0
    
    def find_best_move(node):
        max_child = node.children[0]
        max_index = 0
        for i, child in enumerate(node.children):
            if child.wins > max_child.wins:
                max_child = child
                max_index = i

        return max_index

    _, node, N = traverse(node, side=kgp.SOUTH, N=N)
    
    new_best_move = find_best_move(node) 


    return node, N, best_move
    if new_best_move != best_move:
        best_move = new_best_move
        yield 

    print(N)
    # if N > 3380:
    #     print("max?")
    #     node.print_nodes()
    #     return node, best_move
    yield from search_monte_carlo(node, N, best_move)

sys. setrecursionlimit(1200)
board = kgp.Board.parse("<8,0,0,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8>")

print(board)
tree = searchtree(board, kgp.SOUTH)
tree.simuls = 1



best_move = 0
end = time.time() * 1000 + 5000

while time.time() * 1000 < end:
    node, N, best_move = search_monte_carlo(node, N, best_move)
    print(node.state)
    print(best_move)

    