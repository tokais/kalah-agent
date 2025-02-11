import kgp
import math
import random
import time
from enum import Enum

class searchtree:
    def __init__(self, state:kgp.Board, side=kgp.SOUTH):
        self.wins = 0
        self.simuls = 1
        self.state = state
        self.side = side
        self.children = []

    def is_leave(self):
        return self.children == []
    
    def is_final(self):
        if sum(self.state.north_pits) + sum(self.state.south_pits) < abs(self.state.north - self.state.south):
            return True
        return False
    
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

def evaluate(state, side=kgp.SOUTH):
    # not sure which eval is better 
    return (1 if (state[not side] - state[side]) > 0 else 0)
    return state[side] - state[not side]


class MCTS:

    class Evaluation(Enum):
        BINARY = 1
        DIFFERENCE = 2

    class Effort(Enum):
        RANDOM = 1
        GREEDY = 2

    def __init__(self, evaluation=Evaluation.DIFFERENCE, effort=Effort.RANDOM):
        if evaluation == MCTS.Evaluation.BINARY:
            self.evaluate = (lambda state, side: 1 if (state[not side] - state[side]) > 0 else 0)
        elif evaluation == MCTS.Evaluation.DIFFERENCE:
            self.evaluate = (lambda state, side: state[side] - state[not side])
        else:
            raise("Invalid evaluation type")
        
        self.effort = effort


    def search_monte_carl(self, node, N, max_player_side):

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
                        # evaluate depending on which side is the maximizing player
                        return evaluate(node.state, max_player_side), node, N  
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
            if self.effort == MCTS.Effort.RANDOM:
                return rollout_random(state, side, depth)
            elif self.effort == MCTS.Effort.GREEDY:
                return rollout_greedy(state, side, depth)

        def rollout_greedy(state, side, depth = 0):
            '''full rollout - play a leave state with greedy play till end
                returns: evaluation:int'''
            if state.is_final():
                return self.evaluate(state, max_player_side)   
            
            best_move = -1
            best_score = -1000
            best_move_again = False
            best_move_state = None

            for move in state.legal_moves(side):
                after, again = state.sow(side, move)
                score = self.evaluate(after, side)
                if score > best_score:
                    best_score = score
                    best_move = move
                    best_move_again = again
                    best_move_state = after
            
            if best_move_again:
                return rollout_greedy(best_move_state, side, depth + 1)
            else:
                return rollout_greedy(best_move_state, not side, depth + 1)

 
        def rollout_random(state, side, depth = 0):
            '''full rollout - play a leave state with random play till end
                returns: evaluation:int'''
            if state.is_final():
                return self.evaluate(state, max_player_side)   
            
            move = random.choice(state.legal_moves(side))
            after, again = state.sow(side, move)

            if again:
                return rollout_random(after, side, depth + 1)   
            else:
                return rollout_random(after, not side, depth + 1)

        
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


def mcts_move_arena(mcts_func, state:kgp.Board, move_time:int, side, tree:searchtree):
    '''simulates mcts move
        returns new tree and new state'''
    tree = tree.find_node(state)
    if tree is None:
        print("started new tree")
        tree = searchtree(state, side)
        tree.simuls = 1
    N = tree.simuls
    new_tree = copy.deepcopy(tree)

    again = True


    while again:
        best_move = 0
        end = time.time() + move_time  

        while time.time() < end:
            new_tree, N, new_best_move = mcts_func(new_tree, N, side)
            if new_best_move != best_move:
                best_move = new_best_move
                print(best_move, end=" ")

        new_tree=new_tree.children[best_move]
        
        print(f"calculated {N} moves")
        print(new_tree.side)
        print(new_tree.state)

        if new_tree.state.is_final():
            again = False
        elif new_tree.side != side:
            again = False
        else:
            print("Calculating another move ...")

    return new_tree, new_tree.state


def bot_move_agent(search_func, tree, best_move):
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
    best_move = -1
    myMCTS = MCTS(MCTS.Evaluation.DIFFERENCE, MCTS.Effort.RANDOM)
    
    while True:
        tree, new_best_move, again = bot_move_agent(myMCTS.search_monte_carl, tree, 1)
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



