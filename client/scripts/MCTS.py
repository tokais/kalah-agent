import kgp
import math
import random
import sys
import time
import copy


def evaluate(state):
    # not sure which eval is better 
    return (1 if (state[kgp.SOUTH] - state[kgp.NORTH]) > 0 else 0)
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
    
    def find_node(self, state):
        '''finds a node in the tree with the given state, functions may get optimized'''
        if self.state == state:
            return self
        for child in self.children:
            found = child.find_node(state)
            if found:
                return found
        return None


    def print_nodes(self, depth=0):
        print(self.state)
        print(f"D: {depth}, S: {self.simuls}, W: {self.wins}")
        if self.is_leave():
            return 
        for child in self.children:
            print(f"S: {child.simuls}, W: {child.wins}")
        best = max(self.children, key=lambda x: x.wins)
        best.print_nodes(depth +1)


def search_monte_carl(node, N, side):

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


    def get_best_ucb_child(node, N, c):
        ''' selects child with best upper confident bound - 
            balances between exploration and exploitation
            returns: child: searchtree'''
        
        ucbs = []
        for child in node.children: 
            if child.simuls == 0:       # the ucb would be infinity 
                ucbs = [(child, 1000)]
                break
            score = child.wins if node.side == kgp.SOUTH else child.simuls - child.wins # unsure
            ucb = (score/child.simuls) + c * math.sqrt(math.log(N)/child.simuls)
            ucbs.append((child, ucb))

        return max(ucbs, key=lambda ent: ent[1])[0]


    def traverse(node: searchtree, N, c=2):
        '''traverses the known tree until it finds a child node
            returns: (evaluation: int, node: searchtree, simulations: int)'''

        if node.is_leave():
            if node.simuls > 0:   
                if node.state.is_final():
                      return evaluate(node.state), node, N  
                node.children = expand_children(node)
            else:
                res = rollout(node.state, node.side)
                node.wins += res
                node.simuls += 1
                return res, node, N
        
        bestchild = get_best_ucb_child(node, N, c)
        res, _, N = traverse(bestchild, N + 1, c)
        node.wins += res #backtracking
        node.simuls += 1
        return res, node, N


    def rollout(state, side, depth = 0):
        '''full rollout - play a leave state with random play till end
            returns: evaluation:int'''
        if state.is_final():
            return evaluate(state)   
        
        move = random.choice(state.legal_moves(side))
        after, again = state.sow(side, move)

        if again:
            return rollout(after, side, depth + 1)   
        else:
            return rollout(after, not side, depth + 1)

    
    def find_best_move(node):
        max_child = node.children[0]
        max_index = 0
        for i, child in enumerate(node.children):
            if child.wins > max_child.wins:
                max_child = child
                max_index = i

        return max_index

    _, node, N = traverse(node, N=N)
    if node.children == []:
        print("ALERT")
    best_move = find_best_move(node) 

    return (node, N, best_move)



def bot_move_agent(tree, best_move):
    N = 1
    tree, N, best_move = search_monte_carl(tree, N, kgp.SOUTH)

    # print(tree.state)
    # print(best_move)

    # print(f"calculated {N} moves")
    # tree=tree.children[best_move]

    # print(tree.state)
    again = not tree.side 

    return tree, best_move, again




def mcts_agent(state):
    print(state)
    tree = searchtree(state, kgp.SOUTH)
    tree.simuls = 1
    best_move = -1
    while True:
        tree, new_best_move, again = bot_move_agent(tree, 1)
        if new_best_move != best_move:
            best_move = new_best_move
            # print(best_move)
            yield new_best_move

# if __name__ == "__main__":
#     kgp.connect(mcts_agent, 
#                 host="localhost", 
#                 port=2671, 
#                 debug=True, 
#                 token="HelpHelp", 
#                 authors = ["Firevince"],
#                 name="MCTS Meine Schönheit")
    # kgp.connect(mcts_agent, host    = "wss://kalah.kwarc.info/socket",
    #                    token   = "CCCCCCCCC",
    #                    debug   = True,
    #                    authors = ["Firevince"],
    #                    name    = "FireFire")



