import networkx as nx
from timeit import default_timer as timer
import numpy as np
from .Error import InfeasibleError

class Model:
    def __init__(self):
        self.subscribe_list_on = []
        self.subscribe_list_func = []
        self.nof_calls = 0

    def subscribe(self,on,func,*args):
        self.subscribe_list_on.append(on['idx'])
        self.subscribe_list_func.append((func,args))

    def solve(self):
        try:
            self.fire(np.full(self.search_space.shape, True, dtype=bool))
        except InfeasibleError as e:
            print(e)
            exit(2)

    def fire(self,idx):
        i = 0
        self.changed = np.full(self.changed.shape, False, dtype=bool)
        for lidx in self.subscribe_list_on:
            if np.any(np.logical_and(lidx,idx)):
                func = self.subscribe_list_func[i][0]
                args = self.subscribe_list_func[i][1]
                try:
                    func(*args)
                except InfeasibleError as e:
                    raise e
                self.nof_calls += 1

            i += 1

        if np.any(self.changed):
            try:
                self.fire(self.changed)
            except InfeasibleError as e:
                raise e

    def build_search_space(self,grid,values,no_val=0):
        self.search_space = np.empty(grid.shape,dtype=dict)
        self.changed = np.full(grid.shape, False, dtype=bool)

        no_val_idx = np.where(grid == no_val)
        no_val_idx_invert = np.where(grid != no_val)
        self.search_space[no_val_idx] = {'values':values[:]}
        for idx in np.transpose(no_val_idx_invert):
            t_idx = tuple(idx)
            self.search_space[t_idx] = {'value':grid[t_idx]}


    def check_constraint(self,opts,operator):
            if operator == "alldifferent":
                # check feasibility
        #         print("values: ",values)
                ss_idx = opts['idx']
                # build a graph with connects the variables with the possible values
                G = nx.MultiDiGraph()
                values = self.search_space[ss_idx]

                possible = np.empty((len(values)),dtype=dict)
                already_know = {}
                for i in range(len(values)):
                    if 'values' in values[i]:
                        for j in values[i]['values']:
                            G.add_edge('x_'+str(i),j)
                    else:
                        G.add_edge('x_'+str(i),values[i]['value'])
                        already_know[i] = 1

                # get the maximum matching of this graph
                matching = nx.bipartite.maximum_matching(G)
#                 print(matching)

                n_matching = []
                GM = nx.DiGraph()
                for k in matching:
                    if str(k)[:2] == 'x_':
                        n_matching.append({k:matching[k]})
                        GM.add_edge(k,matching[k])
                        possible[int(k[2:])] = {'values':set([matching[k]])}

                if len(n_matching) < len(values):
                    raise InfeasibleError("Infeasible","The model is infeasible")


                for e in G.edges():
                    if not GM.has_edge(e[0],e[1]):
                        GM.add_edge(e[1],e[0])

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
                new_knowledge = [False]*len(values)
                i = 0
                for p in possible:
                    l = list(p['values'])
                    if len(l) == 1:
                        new_possible.append({'value':l[0]})
                        if i not in already_know:
                            new_knowledge[i] = True
                    else:
                        new_possible.append({'values':l[:]})
                        if len(l)<len(values[i]['values']):
                            new_knowledge[i] = True

                    i += 1

                old_changed = self.changed.copy()
                self.changed[ss_idx] = new_knowledge
                self.changed = np.logical_or(self.changed,old_changed)

                self.search_space[ss_idx] = new_possible

    def get_solution(self):
        grid = [[0]*9 for i in range(9)]
        for r in range(len(self.search_space)):
            for c in range(len(self.search_space[r])):
                if 'value' in self.search_space[r][c]:
                    grid[r][c] = self.search_space[r][c]['value']
        return grid

    def print_search_space(self):
        for r in range(len(self.search_space)):
            row = []
            for c in range(len(self.search_space[r])):
                if 'value' in self.search_space[r][c]:
                    row.append(self.search_space[r][c]['value'])
                else:
                    row.append(self.search_space[r][c]['values'])
            print(row)


