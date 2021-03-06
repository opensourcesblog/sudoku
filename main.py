import networkx as nx
from timeit import default_timer as timer
import numpy as np
from Modules.Model import Model
from Modules.Error import InfeasibleError
import sys

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
    f = open(sys.argv[1], "r")
    lines = f.readlines()
    f.close()
    c = 0
    for line in lines:
        grid[c] = list(map(int, line.split()))
        c += 1

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

    # per block
    for r in range(3):
        for c in range(3):
            bxl,bxr,byt,byb = r*3,(r+1)*3,c*3,(c+1)*3
            idx = np.full(grid.shape, False, dtype=bool)
            idx[bxl:bxr,byt:byb] = True
            model.subscribe({'idx':idx},model.check_constraint,{'idx':idx},"alldifferent")


    model.solve()
#     model.print_search_space()
    solution = model.get_solution()

    print_sudoku(solution)
    print("finished in ",timer()-start)
    print("nof function calls", model.nof_calls)

if __name__ == '__main__':
    main()


