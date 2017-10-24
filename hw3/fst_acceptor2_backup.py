#process carmel file into graph

#For next time, I could use a proper priority queue...rather than a queue that is sort of by priority and it would improve performance
#I don't built the graph until search since it would be inefficient to build it when so many states may never be visited

#
import operator
from collections import defaultdict, deque

import sys

import re


class Graph:
    def __init__(self, start=None, finish=None, transitions=defaultdict(dict)):
        self.transitions = transitions
        self.start = Node(start,('**','**',1)) ## initialise predecessor of start to symbols so know when find it (and can distinguish from other Nones)
        self.finish = Node(finish,probability=0)
        self.nodes = {start:self.start, finish:self.finish} #dict of label: Node object

    def __str__(self):
        return 'A graph with Start: {} Finish: {}\nTransitions: {}'.format(self.start,self.finish,self.transitions)

    def get_start(self):
        return self.start

    def get_finish(self):
        return self.finish

    def get_nodes(self,label):
        return self.nodes[label]

    def get_transitions(self):
        return self.transitions

class Node:
    def __init__(self, label, predecessor=None, probability=1):
        self.label = label
        self.probability = probability #distance from start or probability from start
        self.predecessor = predecessor #this will very importantly be a tuple of (node object,output from transition,probability of transition (NOT TOTAL PROBABILITY)
        # MAKE SURE OK THAT NOT TOTAL - Nope it needs to be total probability
        #self.neighbours = defaultdict(dict) #indexed by key

    def __str__(self):
        return 'Node: {}'.format(self.label)

    def get_probability(self):
        return self.probability

    def get_predecessor(self):
        return  self.predecessor

#    REPLACE ALL PREDECESSOR AND PROBABILITY SHIT WITH THE STATE TABLE

def dijkstra_viterbi(input,graph): #input is assumed to be a string, graph is a Graph Object

    #Initialise backtrace table (state_table) with a nested dictionary to keep track
    #of each state at each timestep, which is to say, at each index.
    state_table = defaultdict(defaultdict)
    #initialise queue
    search_states = deque()
    end_of_input = len(input)  # an imaginary "end of input" index, basically a STOP index
    #add start
    start = graph.get_start()
    finish = graph.get_finish()
    next_index = 0 #start to look at input string
    start_predecessor = ('**', '**', 1)
    winner = None
    final_output = []  # to store eventual output

    #initialise
    update_state_table(state_table, start_predecessor, start, next_index)
    search_states.append((start, next_index))
    #current_node = None
    while search_states:
        current_node, next_index = search_states.popleft() #this will first be the start, then FIFO ordered by priority. FIFO is maybe not the best way to do this but it's a first go since it's simpler
        #update_state_table(state_table, predecessor, current_node, next_index) #maybe this should be index-1?
        if accept_state(current_node, next_index, finish, end_of_input): #input is done and node is a finish node
            winner = current_node
            #update_state_table(state_table, predecessor, winner, next_index)
            break
        #if we are not in a finish state
        #if transitions from node on input then update current node with neighborus, and push the neighbours onto the queue in order of priority
        try:
            neighbours = graph.transitions[current_node.label][input[next_index]] #a dict of (node,output):prob (tuple:float)
            # initialise new nodes based on transition dict data, and the possible neighbours for a given input
            for entry in sorted(neighbours.items(), key=operator.itemgetter(1), reverse=True): #1 is the index of the transition probability, sort in descending order
                label, output, prob = entry[0][0], entry[0][1], entry[1]
                prev_state_prob = state_table[current_node][next_index][2]
                new_prob = prob*prev_state_prob #the probability after taking this transition, so of having reached this next node on this input
                next_node_predecessor = (current_node, output, new_prob)
                try:
                    existing_node = graph.get_nodes(label)
                    next_node = existing_node
                except KeyError: #if node doesn't exist, create it and add it to the graph's nodes
                    next_node = Node(label, next_node_predecessor, new_prob)
                    graph.nodes[label] = next_node
                update_state_table(state_table, next_node_predecessor, next_node, next_index+1)
                search_states.append((next_node, next_index+1)) #append the node found and the next index to look at

        except KeyError:
            continue #if there is nothing to be done on the available input, continue the loop to try the rest of the queue
        except IndexError:  #need something here so that if reached end of input and didn't accept, doesn't end up with index out of range errors
            #break
            continue

    if winner:
        winner_prob = state_table[winner][end_of_input][2]
        return backtrace(winner, end_of_input, final_output, state_table), winner_prob #return result of recursive backtrace and probability, round to 3 sig figs
        #also will have to return probability

    else:
        return '*none*', 0 #return none and zero probability

def backtrace(node, index, final_output, state_table): #traces back through the paths from state_table generated by dijkstra_viterbi and returns the output
    predecessor = state_table[node][index]
    if predecessor[0] != '**': #symbol for predecessor of start
        prev_node, output_char = predecessor[0], predecessor[1]
        final_output.append(output_char)
        backtrace(prev_node,index-1,final_output,state_table)
    return final_output

def accept_state(current_node, next_index, finish, end_of_input):
    if current_node == finish and next_index == end_of_input:
        return True
    else:
        return False

def update_state_table(state_table, predecessor, current_node, next_index): #can I leave state table out of passing it around? Since it's implicitly global
    '''
    when pop a node off the queue add the predecessor information (state it came from, index it came from, probability)
    to the state table at the point we're looking up (NOT at the predecessor)
    State table is in format {state: {index : predecessor info}}. Should mean that whenever encounter the same
    state at same index, the more probable path to that point will win.
    '''
    #Check if there is an entry at current_node next index in state_table
    try:
        current_value = state_table[current_node][next_index]

        if predecessor[2] > current_value[2]: #comparing the probabilities in the tuples
            state_table[current_node][next_index] = predecessor

    except KeyError:
        state_table[current_node][next_index] = predecessor



'''
example input line from file (S3 (S4 "can"  "NOUN" 0.4))
'''

def strip_carmel_fst_file(input_file):
    with open(input_file, 'rU') as file:
        line_list = [line.strip() for line in skip_pycomments(file)]

    final_state = line_list[0]
    initial_state = strip_line(line_list[1])[0] #grabs first element of the list returned as carmel files
                                                # specify start state as first state in second line of file
    #time to build the transitions
    transitions = defaultdict(dict)
    for line in line_list[1:]:
        if line:
            new_trans = strip_line(line)
            state, input, next_state, output, prob = new_trans[0], new_trans[2], new_trans[1], new_trans[3], float(new_trans[4])
            if not transitions[state]: #if state not in dict then assign a new dict to it
                #Example structure {'1': {'can': {(3, 'AUX'): 0.8}}} -- 3 layers
                transitions[state] = {input:{(next_state,output):prob}} #make sure these dictionary assignments work
            else:
                try:
                    if transitions[state][input]: #check next layer of nesting
                        transitions[state][input][(next_state, output)] = prob
                except KeyError:
                    transitions[state][input] = {(next_state,output):prob}

    return [initial_state,final_state,transitions]


def strip_line(line):
    replace_parens = re.sub('(\)|\()',' ',line)
    strip_quotes = re.sub('"','',replace_parens).split()
    return strip_quotes

def skip_pycomments(input):
    for line in input:
        line = line.strip()
        if line:
            if not line.lstrip().startswith('#'):
                yield line

if __name__ == "__main__":
    input_fst = sys.argv[1]
    input_file = sys.argv[2]
    graph_data = strip_carmel_fst_file(input_fst)
    #print(new_graph)
    with open(input_file, 'rU') as file:
        line_list = [line.strip() for line in skip_pycomments(file)]
        for line in line_list:
            line_as_string = re.sub('"', '', line).strip().split()
            result, prob = dijkstra_viterbi(line_as_string, Graph(*graph_data))

            if isinstance(result,list): #reverse before returning, unless failed and result was string *none*
                result.reverse()
                result = '"'+'" "'.join(result)+'"' #make it look like it is carmel

            print('{} => {} {:g}'.format(line.strip(), result, prob))
            #break #this is there temporarily to do only one line

###NEED TO ADD DEFAULT VALUES to make sure that if no probabilities are given, assume P = 1
