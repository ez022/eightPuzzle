import math
import heapq
import time


solution_depth = 0;
numNodes_expanded = 0;
max_queue_size = 0;

def print_matrix(pState):
    for r in pState:
        print(r)

def print_node(psNode):
    print("==>State: ")
    print_matrix(psNode.pState)
    print("==>g(): ", psNode.g, ", h(): ", psNode.h, ", f(): ", psNode.g+psNode.h)


def create_solution(n):
    # create solution state for n*n puzzle
    return [[(i * n + j + 1) % (n * n) for j in range(n)] for i in range(n)]

def format_sample_input(n):
    # generate sample input string
    example_puzzle = create_solution(n)

    last_row = example_puzzle[-1]

    last_row[-1], last_row[-2] = last_row[-2], last_row[-1]
    return '||'.join(' '.join(map(str, row)) for row in example_puzzle)

def validate_puzzle_input(puzzle_input, n):
    #make sure the input numbers are reasonable, ie each int appears once
    expected_set = set(range(n * n))
    input_set = {num for row in puzzle_input for num in row}
    if input_set != expected_set:
        raise ValueError("Puzzle must contain each number from 0 to {} exactly once.".format(n * n - 1))

def get_search_method():

    while True:
        method_type = input("Which search method would you like to use? Please enter 1 for Uniform Cost Search; 2 for A* with Misplaced Tile Heuristic; 3 for A* with Manhattan Distance Heuristic: ")
        try:
            m = int(method_type)
            if m not in [1,2,3]:
                raise ValueError("Please enter a valid number")
            return m
        except ValueError as e:
            print(f"Invalid input: {e}. Please try again.")

def get_puzzle_size():

    #make sure puzzle size reasonable, eg 8, 17, 24, etc

    while True:
        puzzle_type = input("What puzzle would you like to solve? Enter the number of tiles (eg 8 for 8-puzzle): ")
        try:
            num_tiles = int(puzzle_type)
            n = int(math.sqrt(num_tiles + 1))
            #print("n is ",n)
            if n * n != num_tiles + 1 or n==1:
                raise ValueError("The number of tiles must be n^2 - 1 for some integer n>1 (eg 8, 15, 24)")
            return n
        except ValueError as e:
            print(f"Invalid input: {e}. Please try again.")

def get_puzzle(sample_input,n):
    while True:
        #ask user to enter puzzle
        puzzle_input = input(f"Please enter puzzle for a {n}x{n} grid. Use spaces to separate numbers and '||' to separate rows. (eg. '{sample_input}'): ")
        
        # Process the input into a list of lists
        try:
            puzzleState = [[int(num) for num in r.split()] for r in puzzle_input.split("||")]
            if len(puzzleState) != n or any(len(row) != n for row in puzzleState):
                raise ValueError("The puzzle format does not match specified size.")
            validate_puzzle_input(puzzleState, n)
        except ValueError as e:
            print(f"Invalid format: {e}. Please try again.")
            continue    

        return puzzleState    

class psNode:
    def __init__(self, pState, g, h=0):
        self.pState = pState
        self.g = g
        self.h = h

    def __str__(self):
        return f"State: {self.pState}, Cost: {self.g}"

    def getSum(self):
        return self.g + self.h

    def __lt__(self,other):
        #compare based on h; used to break ties;
        return self.h<other.h
       

def get_f(psNode,sol):
    return psNode.g

def get_misplaced_tiles(pState,sol, n):
    #sol = create_solution(n)
    mt = 0
    for i in range(n):
        for j in range(n):
            if pState[i][j]!=sol[i][j] and pState[i][j]!=0:
                mt+=1
    return mt

def get_manhattan_distance(pState,sol,n):
    #get position where it's supposed to be
    sol_dict = {sol[i][j]:(i,j) for i in range(n) for j in range(n) if sol[i][j]!=0}
    num_moves = 0

    for i in range(n):
        for j in range(n):
            tile = pState[i][j]
            if tile != 0:
                sol_x, sol_y = sol_dict[tile]
                num_moves+=abs(sol_x-i)+abs(sol_y-j)
    
    return num_moves


def make_move(pState, tile_row, tile_col, zero_row, zero_col):
    new_pState = [r[:] for r in pState]
    #print("copied new pstate is ", new_pState)
    new_pState[zero_row][zero_col] = pState[tile_row][tile_col]
    new_pState[tile_row][tile_col] = pState[zero_row][zero_col]
    return new_pState
   

def expand_node(psNode,n):
    curState = psNode.pState
    for i, r in enumerate(curState):
        if 0 in r:
            zero_row = i
            zero_col = r.index(0)
            break
    
    newState_list = []
    if zero_row>0: 
        #swap with above;
        newState_list.append(make_move(curState,zero_row-1,zero_col,zero_row,zero_col))
    if zero_row<n-1:
        #swap with below;
        newState_list.append(make_move(curState,zero_row+1,zero_col,zero_row,zero_col))
    if zero_col>0:
        #swap with left;
        newState_list.append(make_move(curState,zero_row,zero_col-1,zero_row,zero_col))
    if zero_col<n-1:
        #swap with right;
        newState_list.append(make_move(curState,zero_row,zero_col+1,zero_row,zero_col))
    
    #print("new state list is ", newState_list)
    return newState_list    



def uniform_cost_search(initialState,sol,n):
    global solution_depth;
    global numNodes_expanded;
    global max_queue_size;
    hq = []
    expanded_set = set()
    iniNode = psNode(pState=initialState,g=0)
    heapq.heappush(hq,(0,iniNode))
    print("Now, let's solve it.")
    while True:
        if len(hq)>max_queue_size:
            max_queue_size = len(hq)
        if not hq:# queue is empty
            return False
        
        #pop lowest f
        newNode = heapq.heappop(hq)[1]
        #print("new node is")
        #print_node(newNode)
        #check if it's goal state
        solution_depth = newNode.g
        print("The best state to explore is ")
        print_node(newNode)
        if newNode.pState == sol:
            return newNode.pState

        cur_g = newNode.g
        print("It is not the goal state. We will expand it and add child nodes to the queue.")
        nextStates = expand_node(newNode,n)
        numNodes_expanded+=1
        #print("next states is ", nextStates)
        
        psTuple = tuple(tuple(l) for l in newNode.pState)
        expanded_set.add(psTuple)

        #print("child states are ",nextStates)
        #check for repeated;
        for s in nextStates:
            #skip if already expanded
            sTuple = tuple(tuple(l) for l in s)
            if sTuple in expanded_set:
                print("A child state skipped because of repeated state")
                continue
            
            #make node
            chNode = psNode(pState=s,g=cur_g+1)
            #push to h
            heapq.heappush(hq,(chNode.g,chNode))

def misplaced_tile_heuristic(initialState,sol,n):
    global solution_depth;
    global numNodes_expanded;
    global max_queue_size;
    hq = []
    expanded_set = set()
    hval = get_misplaced_tiles(initialState,sol, n)
    iniNode = psNode(pState=initialState,g=0, h=hval)
    heapq.heappush(hq,(iniNode.getSum(),iniNode))
    print("Now, let's solve it.")
    while True:
        if len(hq)>max_queue_size:
            max_queue_size = len(hq)
        if not hq:# queue is empty
            return False
        
        #pop lowest f
        newNode = heapq.heappop(hq)[1]
        #print("new node is")
        #print_node(newNode)
        #check if it's goal state
        solution_depth = newNode.g
        print("The best state to explore is ")
        print_node(newNode)
        if newNode.pState == sol:
            return newNode.pState

        cur_g = newNode.g
        print("It is not the goal state. We will expand it and add child nodes to the queue.")
        nextStates = expand_node(newNode,n)
        numNodes_expanded+=1
        #print("next states is ", nextStates)
        
        psTuple = tuple(tuple(l) for l in newNode.pState)
        expanded_set.add(psTuple)

        #print("child states are ",nextStates)
        #check for repeated;
        for s in nextStates:
            #skip if already expanded
            sTuple = tuple(tuple(l) for l in s)
            if sTuple in expanded_set:
                print("A child state skipped because of repeated state")
                continue
            
            #make node

            chNode = psNode(pState=s,g=cur_g+1,h=get_misplaced_tiles(initialState,sol, n))
            #push to h
            heapq.heappush(hq,(chNode.getSum(),chNode))

def manhattan_distance_heuristic(initialState,sol,n):
    global solution_depth;
    global numNodes_expanded;
    global max_queue_size;
    hq = []
    expanded_set = set()
    hval = get_manhattan_distance(initialState,sol, n)
    iniNode = psNode(pState=initialState,g=0, h=hval)
    heapq.heappush(hq,(iniNode.getSum(),iniNode))
    print("Now, let's solve it.")
    while True:
        if len(hq)>max_queue_size:
            max_queue_size = len(hq)
        if not hq:# queue is empty
            return False
        
        #pop lowest f
        newNode = heapq.heappop(hq)[1]
        #print("new node is")
        #print_node(newNode)
        #check if it's goal state
        solution_depth = newNode.g
        print("The best state to explore is ")
        print_node(newNode)
        if newNode.pState == sol:
            return newNode.pState

        cur_g = newNode.g
        print("It is not the goal state. We will expand it and add child nodes to the queue.")
        nextStates = expand_node(newNode,n)
        numNodes_expanded+=1
        #print("next states is ", nextStates)
        
        psTuple = tuple(tuple(l) for l in newNode.pState)
        expanded_set.add(psTuple)

        #print("child states are ",nextStates)
        #check for repeated;
        for s in nextStates:
            #skip if already expanded
            sTuple = tuple(tuple(l) for l in s)
            if sTuple in expanded_set:
                print("A child state skipped because of repeated state")
                continue
            
            #make node

            chNode = psNode(pState=s,g=cur_g+1,h=get_manhattan_distance(initialState,sol, n))
            #push to h
            heapq.heappush(hq,(chNode.getSum(),chNode))


def main():


    n = get_puzzle_size()

    #create solution based on n
    solState = create_solution(n)

    # generate sample input
    sample_input = format_sample_input(n)

    puzzleState = get_puzzle(sample_input,n)

    method_type = get_search_method()
    #print("method type is: ", method_type)

    print("The puzzle you entered is: ")
    #print(puzzleState)
    print_matrix(puzzleState)

    start_time = time.time()
    if method_type==1:
        print("Uniform Cost Search")
        result = uniform_cost_search(puzzleState,solState,n)
    elif method_type==2:
        print("A* with Misplaced Tile Heuristic")
        result = misplaced_tile_heuristic(puzzleState,solState,n)
    elif method_type==3:
        print("A* with Manhattan Distance Heuristic")
        result = manhattan_distance_heuristic(puzzleState,solState,n)

    #result = uniform_cost_search(puzzleState,solState,n)
    #result = misplaced_tile_heuristic(puzzleState,solState,n)
    #result = manhattan_distance_heuristic(puzzleState,solState,n)


    end_time = time.time()
    time_elapsed = end_time-start_time
    if result:
        print("It is the goal state. Puzzle solved!")
        print_matrix(result)
        print("Solution depth is: ", solution_depth)
        print("Number of nodes expanded is: ", numNodes_expanded)
        print("Max queue size is: ", max_queue_size)
        print(f"Elapsed time is: {time_elapsed} seconds")

    else:
        print("Puzzle cannot be solved")    
        print("Depth explored is: ", solution_depth)
        print("Number of nodes expanded is: ", numNodes_expanded)
        print("Max queue size is: ", max_queue_size)
        print(f"Elapsed time is: {time_elapsed} seconds")


if __name__ == "__main__":
    main()
