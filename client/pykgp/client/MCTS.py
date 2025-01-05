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

def bot_move(tree, N):
    new_tree = copy.deepcopy(tree)
    again = True
    while again:
        best_move = 0
        end = time.time() + 3   
        while time.time() < end:
            new_tree, N, new_best_move = search_monte_carl(new_tree, N)
            if new_best_move != best_move:
                best_move = new_best_move
                # print(new_tree.state)
                # print(best_move)
        # print(f"calculated {N} moves")
        new_tree=new_tree.children[best_move]
        # print(new_tree.state)
        if new_tree.side == kgp.NORTH:
            again = False
        # else:
        #     print("Calculating another move ...")

    return new_tree

def bot_move_agent(tree, best_move):
    N = 1
    tree, N, best_move = search_monte_carl(tree, N)

    # print(tree.state)
    # print(best_move)

    # print(f"calculated {N} moves")
    # tree=tree.children[best_move]

    # print(tree.state)
    again = not tree.side 

    return tree, best_move, again

def player_move(tree):
    new_tree = copy.deepcopy(tree)
    mymove = None
    while mymove == None :
        try:
            mymove = input("Choose your move: ")
            mymove = int(mymove) - 1
        except:
            mymove = None
            print("not a number")
            continue
        if mymove < 0 or mymove >= new_tree.state.size or not new_tree.state.is_legal(kgp.NORTH, mymove):
            mymove = None
            print("not a legal move")
            continue
        
        state, again = new_tree.state.sow(kgp.NORTH, mymove)
        for i in range(int(mymove)):
            if not new_tree.state.is_legal(kgp.NORTH, i):
                mymove -= 1

        if again:
            if new_tree.children == []:
                print("started new tree")
                new_tree = searchtree(state, kgp.SOUTH)
            else:
                new_tree = new_tree.children[int(mymove)]
            mymove = None
            print("you have another turn")
            print(new_tree.state)
     
    new_tree = new_tree.children[int(mymove)]
    if new_tree.state:
        print(new_tree.state)
    elif new_tree.state.is_final():
        input("Game ended")
    return new_tree

def play_interactive():
    board = kgp.Board.parse("<8,0,0,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8>")
    tree = searchtree(board, kgp.SOUTH)
    tree.simuls = 1
    N = 1

    while True:
        tree = bot_move(tree, N)
        tree = player_move(tree)


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

if __name__ == "__main__":
    # kgp.connect(mcts_agent, 
    #             host="localhost", 
    #             port=2671, 
    #             debug=True, 
    #             token="HelpHelp", 
    #             authors = ["Firevince"],
    #             name="MCTS Meine Schönheit")
    kgp.connect(mcts_agent, host    = "wss://kalah.kwarc.info/socket",
                       token   = "CCCCCCCCC",
                       debug   = True,
                       authors = ["Firevince"],
                       name    = "FireFire")

# if __name__ == "__main__":
#     play_interactive()

