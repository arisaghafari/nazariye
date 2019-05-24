from collections import defaultdict
from disjoint_set import DisjointSet

import networkx as nx
from graphviz import Source


class DFA_min(object):
    def __init__(self, states_or_filename, terminals=None, start_state=None,transitions=None, final_states=None):


        file_r = open("output1.txt", "r")
        file_w = open("input2.txt", "w")

        r_lines = file_r.readlines()
        # print(int(r_lines[0]))
        for i in range(int(r_lines[0])):
            if i==int(r_lines[0])-1:
                file_w.write(str(i) +"\n" )
                break
            file_w.write(str(i)+" ")

        # print(r_lines[1])
        r_lines[1] = r_lines[1].split(",")
        r_lines[1] = " ".join(r_lines[1])
        # print(r_lines[1])

        file_w.write(r_lines[1])

        # print(r_lines)

        final_list=[]
        for i in range (2,len(r_lines)):

            r_lines[i] = r_lines[i].split(",")




            for j in range(3):
                if r_lines[i][0][0]=="-" and r_lines[i][0][1]==">" :
                    # print(i)
                    # print(len(r_lines[i][0]))
                    if r_lines[i][0][2]=="*":
                        start= r_lines[i][0][4]

                        if r_lines[i][0][4] not in final_list:
                            final_list.append(r_lines[i][0][4])

                if r_lines[i][0][0]=="*":
                    if r_lines[i][0][2] not in final_list:
                        final_list.append(r_lines[i][0][2])

                if len(r_lines[i][0])>1:
                    r_lines[i][0]=r_lines[i][0][-1]

                if i==len(r_lines)-1:
                    if len(r_lines[i][2]) > 1:
                        r_lines[i][2] = r_lines[i][2][-2]

                elif len(r_lines[i][2])>1:
                    r_lines[i][2]=r_lines[i][2][-2]

        r_lines=r_lines[2:]
        # print(r_lines)
        # print(final_list)
        # print(start)

        file_w.write(start+"\n")

        file_w.write(str(len(final_list))+" ")
        for i in range(len(final_list)):
            if i==len(final_list)-1:
                file_w.write(final_list[i]+"\n")
                break
            file_w.write(final_list[i]+" ")

        for i in range(len(r_lines)):
            if i ==len(r_lines)-1:
                file_w.write(r_lines[i][0] + " " + r_lines[i][1] + " " + r_lines[i][2])
                break
            file_w.write(r_lines[i][0]+" "+r_lines[i][1]+" "+r_lines[i][2]+"\n")

        file_w.close()
        file_r.close()


        if terminals is None:
            self._get_graph_from_file(states_or_filename)
        else:
            assert isinstance(states_or_filename, list) or \
                   isinstance(states_or_filename, tuple)
            self.states = states_or_filename

            assert isinstance(terminals, list) or isinstance(terminals, tuple)
            self.terminals = terminals

            assert isinstance(start_state, str)
            self.start_state = start_state

            assert isinstance(transitions, dict)
            self.transitions = transitions

            assert isinstance(final_states, list) or \
                   isinstance(final_states, tuple)
            self.final_states = final_states

    def draw(self):
        '''
        Draws the dfa using networkx and matplotlib
        '''
        g = nx.DiGraph()

        for x in self.states:
            g.add_node(x, shape='doublecircle' if x in self.final_states else 'circle',
                       fillcolor='grey' if x == self.start_state else 'white', style='filled')

        temp = defaultdict(list)
        for k, v in self.transitions.items():
            temp[(k[0], v)].append(k[1])

        for k, v in temp.items():
            g.add_edge(k[0], k[1], label=','.join(v))
        return Source(nx.drawing.nx_agraph.to_agraph(g))

    def _remove_unreachable_states(self):
        '''
        Removes states that are unreachable from the start state
        '''


        g = defaultdict(list)

        for k, v in self.transitions.items():
            g[k[0]].append(v)

        # do DFS
        stack = [self.start_state]

        reachable_states = set()

        while stack:
            state = stack.pop()

            if state not in reachable_states:
                stack += g[state]

            reachable_states.add(state)

        self.states = [state for state in self.states \
                       if state in reachable_states]

        self.final_states = [state for state in self.final_states \
                             if state in reachable_states]

        self.transitions = {k: v for k, v in self.transitions.items() \
                            if k[0] in reachable_states}



    def minimize(self):

        self._remove_unreachable_states()

        def order_tuple(a, b):
            return (a, b) if a < b else (b, a)

        table = {}

        sorted_states = sorted(self.states)

        # initialize the table
        for i, item in enumerate(sorted_states):
            for item_2 in sorted_states[i + 1:]:
                table[(item, item_2)] = (item in self.final_states) != (item_2 \
                                                                        in self.final_states)

        flag = True

        # table filling method
        while flag:
            flag = False

            for i, item in enumerate(sorted_states):
                for item_2 in sorted_states[i + 1:]:

                    if table[(item, item_2)]:
                        continue

                    # check if the states are distinguishable
                    for w in self.terminals:
                        t1 = self.transitions.get((item, w), None)
                        t2 = self.transitions.get((item_2, w), None)

                        if t1 is not None and t2 is not None and t1 != t2:
                            marked = table[order_tuple(t1, t2)]
                            flag = flag or marked
                            table[(item, item_2)] = marked

                            if marked:
                                break

        d = DisjointSet(self.states)

        # form new states
        for k, v in table.items():
            if not v:
                d.union(k[0], k[1])

        self.states = [str(x) for x in range(1, 1 + len(d.get()))]
        new_final_states = []
        self.start_state = str(d.find_set(self.start_state))

        for s in d.get():
            for item in s:
                if item in self.final_states:
                    new_final_states.append(str(d.find_set(item)))
                    break

        self.transitions = {(str(d.find_set(k[0])), k[1]): str(d.find_set(v))
                            for k, v in self.transitions.items()}

        self.final_states = new_final_states

        # print(self.final_states, self.start_state)
        # print(self.states)
    def output(self):
        # print(self.terminals)
        # print(self.final_states)
        final_output = open("output2.txt","w")
        L = list(self.transitions.items())
        # print(L)
        final_output.write(str(len(self.states))+"\n")
        for i in range(len(self.terminals)):
            if i==len(self.terminals)-1:
                final_output.write(self.terminals[i]+"\n")
                break
            final_output.write(self.terminals[i]+",")

        final_output.write("->")
        for i in range(len(L)):
            if (L[i][0][0] in self.final_states) and (L[i][1] in self.final_states):
                final_output.write("*q" + L[i][0][0] + "," + L[i][0][1] + "," + "*q" + L[i][1]+"\n")
            elif (L[i][0][0] in self.final_states):
                final_output.write("*q" + L[i][0][0] + "," + L[i][0][1] + "," + "q" + L[i][1]+"\n")
            elif (L[i][1] in self.final_states):
                final_output.write("q" + L[i][0][0] + "," + L[i][0][1] + "," + "*q" + L[i][1]+"\n")

            else:
                final_output.write("q"+L[i][0][0]+","+L[i][0][1]+","+"q"+L[i][1]+"\n")

    def __str__(self):
        '''
        String representation
        '''
        num_of_state = len(self.states)
        start_state = self.start_state
        num_of_final = len(self.final_states)

        return '{} states. {} final states. start state - {}'.format( \
            num_of_state, num_of_final, start_state)

    def _get_graph_from_file(self, filename):
        '''
        Load the graph from file
        '''

        with open(filename, 'r') as f:

            try:
                lines = f.readlines()
                states, terminals, start_state, final_states = lines[:4]

                if states:
                    self.states = states[:-1].split()
                else:
                    raise Exception('Invalid file format: cannot read states')

                if terminals:
                    self.terminals = terminals[:-1].split()
                else:
                    raise Exception('Invalid file format: cannot read terminals')

                if start_state:
                    self.start_state = start_state[:-1]
                else:
                    raise Exception('Invalid file format: cannot read start state')

                if final_states:
                    self.final_states = final_states[:-1].split()
                else:
                    raise Exception('Invalid file format: cannot read final states')

                lines = lines[4:]

                self.transitions = {}

                for line in lines:
                    current_state, terminal, next_state = line[:-1].split()

                    self.transitions[(current_state, terminal)] = next_state

            except Exception as e:
                pass