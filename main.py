import networkx as nx
from timeit import default_timer as timer
import numpy as np
from Modules.Model import Model
from Modules.Error import InfeasibleError

def print_sudoku(grid):
    for r in range(len(grid)):
        row = ""
        for c in range(len(grid[r])):
            if c%3 == 0:
                row += "["
            row += " "+str(grid[r][c])
            if c%3 == 2:
                row += " ]"
        print(row)
        if r % 3 == 2:
            print("-"*27)

def main():
    grid = [[0]*9 for i in range(9)]
    grid[0] = [1,0,0,4,5,0,0,3,0]
    grid[1] = [2,0,0,6,8,0,5,0,0]
    grid[2] = [0,8,5,0,1,0,0,9,0]
    grid[3] = [0,9,7,0,0,0,0,0,2]
    grid[4] = [0,2,0,0,6,1,0,0,0]
    grid[5] = [0,0,0,8,0,0,0,0,0]
    grid[6] = [7,5,2,0,3,0,0,0,9]
    grid[7] = [0,4,0,0,0,0,0,0,3]
    grid[8] = [9,3,0,0,7,0,8,0,0]

#     grid[0] = [1,0,5,0,0,3,4,6,0]
#     grid[1] = [7,0,0,2,4,0,0,0,9]
#     grid[2] = [0,0,0,0,0,0,0,0,0]
#     grid[3] = [6,0,7,0,1,0,0,0,0]
#     grid[4] = [0,0,0,0,8,0,1,0,0]
#     grid[5] = [5,0,9,0,0,6,0,8,7]
#     grid[6] = [3,0,0,0,5,0,2,0,0]
#     grid[7] = [0,0,1,0,0,2,0,4,3]
#     grid[8] = [0,7,8,1,0,0,0,9,0]
#
    grid[0] = [0,2,1,0,7,9,0,8,5]
    grid[1] = [0,4,5,3,1,0,0,0,9]
    grid[2] = [0,7,0,0,4,0,0,1,0]
    grid[3] = [0,0,0,1,0,8,0,3,6]
    grid[4] = [0,6,0,0,0,0,2,0,8]
    grid[5] = [0,0,0,0,0,3,0,0,4]
    grid[6] = [6,0,8,0,0,0,0,0,0]
    grid[7] = [0,9,4,0,0,7,8,0,0]
    grid[8] = [2,0,0,5,0,0,0,4,0]

    grid = np.array(grid)
    print("Start with %d digits" % np.count_nonzero(grid))
    start = timer()


    model = Model()
    model.build_search_space(grid,[1,2,3,4,5,6,7,8,9],0)



    # per row
    for r in range(len(grid)):
        idx = np.full(grid.shape, False, dtype=bool)
        idx[r,:] = True
        model.subscribe({'idx':idx},model.check_constraint,{'idx':idx},"alldifferent")


    # per col
    for c in range(len(grid[0])):
        idx = np.full(grid.shape, False, dtype=bool)
        idx[:,c] = True
        model.subscribe({'idx':idx},model.check_constraint,{'idx':idx},"alldifferent")

    # in block
    for r in range(3):
        for c in range(3):
            bxl,bxr,byt,byb = r*3,(r+1)*3,c*3,(c+1)*3
            idx = np.full(grid.shape, False, dtype=bool)
            idx[bxl:bxr,byt:byb] = True
            model.subscribe({'idx':idx},model.check_constraint,{'idx':idx},"alldifferent")


    model.solve()

    solution = model.get_solution()
    print_sudoku(solution)
    print("finished in ",timer()-start)
    print("nof function calls", model.nof_calls)

if __name__ == '__main__':
    main()


