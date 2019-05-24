from finite_automata import NFA, DFA
from minimization import DFA_min


filename = "input.txt"#input('Enter the name of the NFA file: ')


file = open(filename, 'r')
lines = file.readlines()
file.close()


nfa = NFA()
dfa = DFA()

nfa.construct_nfa_from_file(lines)
dfa.convert_from_nfa(nfa)

dfa.print_dfa()

dfa = DFA_min("input2.txt")
# dfa._get_graph_from_file("input2.txt")
dfa.minimize()
dfa.output()
# dfa.convert_input()