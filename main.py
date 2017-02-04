import networkx as nx

def print_search_space(search_space):
    for r in range(len(search_space)):
        row = []
        for c in range(len(search_space[r])):
            if 'value' in search_space[r][c]:
                row.append(search_space[r][c]['value'])
            else:
                row.append(search_space[r][c]['values'])
        print(row)

def print_by_row(grid):
    for r in range(len(grid)):
        print(grid[r])

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

def build_search_space(grid,values,no_val=0):
    search_space = [[{}]*len(grid[0]) for i in range(len(grid))]

    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if grid[r][c] == no_val:
                search_space[r][c] = {'values':values[:]}
            else:
                search_space[r][c] = {'value':grid[r][c]}

    return search_space

def add_constraint(changed,search_space,values,operator):
    if operator == "alldifferent":
        # check feasibility
#         print("values: ",values)

        # build a graph with connects the variables with the possible values
        G = nx.MultiDiGraph()
        values = values['values']
        possible = [{} for i in range(len(values))]
        already_know = 0
        for i in range(len(values)):
            if 'values' in values[i]:
                for j in values[i]['values']:
                    G.add_edge('x_'+str(i),j)
            else:
                G.add_edge('x_'+str(i),values[i]['value'])
                already_know += 1


#         print("edges: ",G.edges())
        # get the maximum matching of this graph
        matching = nx.bipartite.maximum_matching(G)


        n_matching = []
        GM = nx.DiGraph()
        for k in matching:
            if str(k)[:2] == 'x_':
                n_matching.append({k:matching[k]})
                GM.add_edge(k,matching[k])
                possible[int(k[2:])] = {'values':set([matching[k]])}

        if len(n_matching) < len(values):
            raise "infeasible"


        for e in G.edges():
            if not GM.has_edge(e[0],e[1]):
                GM.add_edge(e[1],e[0])
#         print("matching: ", n_matching)
#         print("l(matching): ", len(n_matching))
        # find even alternating path
        # find free vertex
#         print("GM edges", GM.edges())
        for n in GM.nodes():
            if str(n)[:2] != "x_" and len(GM.predecessors(n)) == 0:
                print("Free vertex: ", n)

        scc = nx.strongly_connected_component_subgraphs(GM)
        for scci in scc:
            for e in scci.edges():
                if str(e[0])[:2] != 'x_':
                    e = (int(e[1][2:]),e[0])
                else:
                    e = (int(e[0][2:]),e[1])
                if 'values' not in possible[e[0]]:
                    possible[e[0]] = {'values': set()}
                possible[e[0]]['values'].add(e[1])

        new_possible = []
        know_now = 0
        for p in possible:
            l = list(p['values'])
            if len(l) == 1:
                new_possible.append({'value':l[0]})
                know_now += 1
            else:
                new_possible.append({'values':l[:]})
        if know_now > already_know:
            changed = True
        return search_space,changed,new_possible
    if operator == "noeq":
        x = values['x']
        y = values['y']
        if 'value' in search_space[x[0]][x[1]] and 'value' in search_space[y[0]][y[1]]:
            return search_space, changed
        if 'value' in search_space[x[0]][x[1]]:
            try:
                search_space[y[0]][y[1]]['values'].remove(search_space[x[0]][x[1]]['value'])
                if len(search_space[y[0]][y[1]]['values']) == 1:
                    search_space[y[0]][y[1]]['value'] = search_space[y[0]][y[1]]['values'][0]
                    del search_space[y[0]][y[1]]['values']
                    return search_space,True
            except:
                pass
            return search_space,changed
        if 'value' in search_space[y[0]][y[1]]:
            try:
                search_space[x[0]][x[1]]['values'].remove(search_space[y[0]][y[1]]['value'])
                if len(search_space[x[0]][x[1]]['values']) == 1:
                    search_space[x[0]][x[1]]['value'] = search_space[x[0]][x[1]]['values'][0]
                    del search_space[x[0]][x[1]]['values']
                    return search_space,True
            except:
                pass
            return search_space, changed
        return search_space,changed

def print_game(search_space):
    total_values = 0
    grid = [[0]*9 for i in range(9)]
    for r in range(len(search_space)):
        for c in range(len(search_space[r])):
            if 'value' in search_space[r][c]:
                grid[r][c] = search_space[r][c]['value']
                total_values += 1
#     print("total value: ", total_values)
    print_sudoku(grid)


def main():
    changed = True
    grid = [[0]*9 for i in range(9)]
#     grid[0] = [1,2,3,4,5,6,7,8,0] # 4
    grid[0] = [1,0,0,4,5,0,0,3,0] # 4
    grid[1] = [2,0,0,6,8,0,5,0,0] # 4
    grid[2] = [0,8,5,0,1,0,0,9,0] # 4
    grid[3] = [0,9,7,0,0,0,0,0,2] # 3
    grid[4] = [0,2,0,0,6,1,0,0,0] # 3
    grid[5] = [0,0,0,8,0,0,0,0,0] # 1
    grid[6] = [7,5,2,0,3,0,0,0,9] # 5
    grid[7] = [0,4,0,0,0,0,0,0,3] # 2
    grid[8] = [9,3,0,0,7,0,8,0,0] # 4
    # total: 30

    search_space = build_search_space(grid,[1,2,3,4,5,6,7,8,9],0)

    while changed:
        changed = False
        # per row
        for r in range(len(grid)):
            search_space,changed,possible = add_constraint(changed,search_space,{'values':search_space[r][:]},"alldifferent")
            search_space[r] = possible

        # per col
        for c in range(len(grid[0])):
            col = [row[c] for row in search_space]
            search_space,changed,possible = add_constraint(changed,search_space,{'values':col},"alldifferent")
            i = 0
            for row in search_space:
                row[c] = possible[i]
                i += 1

        # in block
        for r in range(len(grid)):
            for c in range(len(grid[r])):
                block = []
                for r1 in range(r//3*3,r//3*3+3):
                    for c1 in range(c//3*3,c//3*3+3):
                        block.append(search_space[r1][c1])
                search_space,changed,possible = add_constraint(changed,search_space,{'values':block},"alldifferent")
                i = 0
                for r1 in range(r//3*3,r//3*3+3):
                    for c1 in range(c//3*3,c//3*3+3):
                        search_space[r1][c1] = possible[i]
                        i += 1

    print_game(search_space)

#     print_search_space(search_space)

if __name__ == '__main__':
    main()
