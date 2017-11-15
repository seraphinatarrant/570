'''
A script that implements VIterbi algorithm on an input hmm file of standard hmm format. Note that for this case,
BFS is EXTREMELY slow, (unlike Viterbi for a PFA transducer) so I switched the deque to function as a stack and do DFS.
Then as long as I use a minheap to place the next step on the heap in order of lowest probability first, the first item
I pop off the stack will always be the highest probability and I can terminate search whenever I successfully reach end
of input, and know I have found the true winner.

Command to run: viterby.py input_hmm test_file output_file

test file format: one observation per line, which observations whitespace delimited.
(For POS tagging an observation is a sentence.)
output file format: observation => state_seq logprob where state_seq is best state seq found and logprob is base 10 of
that sequence.


'''
import operator
import sys
from collections import defaultdict, deque
from heapq import heappush, heappop

import math



def update_state_table(state_table, predecessor, current_state, next_index):
    '''
    when pop a node off the queue add the predecessor information (state it came from, probability)
    to the state table at the point we're looking up (NOT at the predecessor)
    State table is in format {state: {index : predecessor info}}. Should mean that whenever encounter the same
    state at same index, the more probable path to that point will win.
    '''
    #Check if there is an entry at current_node next index in state_table
    existing_value = state_table[current_state][next_index]
    if existing_value:
        # comparing the probabilities in the tuples, update only if new value is better
        if predecessor[1] > existing_value[1]:
            state_table[current_state][next_index] = predecessor
    else:
        state_table[current_state][next_index] = predecessor

def viterbi(observation, init_states, transitions, emissions):
    '''
    Use logprobs to avoid underflow
    I made the choice to use FIFO deque to track states and a maxheap to push states onto the queue based on their prob.
    Since at EACH step I want the highest prob, but I don't actually want highest total prob, since then I'll explore
    all nodes with less elements (since longer strings just have lower overall probability)
    :param observation: an observation sequence in a list form
    :param hmm: an hmm with init, trans, emit probs for that sequence.
    :return: winner, the sequence that is highest probability for the observation, and the logprob of winner
    '''
    state_table = defaultdict(lambda: defaultdict(tuple)) #nested to avoid try accepts for keyerrors (which are slow)
    search_states = deque()
    next_index = 0
    end_of_input = len(observation)
    winner = None
    final_sequence = []
    start_predecessor = ('**', 0.0) #default symbols and logprobs. Predecessor is prev state, probability
    #initialise search queue with start states and update state table with start states
    start_states = sorted(init_states.items(), key=operator.itemgetter(1), reverse=True) #sort by highest prob first
    [search_states.append((item[0], next_index, start_predecessor)) for item in start_states]

    while search_states:
        #pop a working state and input position off the queue
        current_state, next_index, predecessor = search_states.pop()
        #update after pop off since then we call the function less often and everything should be faster
        update_state_table(state_table, predecessor, current_state, next_index)
        #find the intersection of possible transitions with valid emissions
        prev_state_prob = state_table[current_state][next_index][1]  # grabs predecessor and prob to here
        if next_index < end_of_input:
            #grab the dict of states that are transition and their prob and the dict of states that emit the observation and their prob
            valid_transitions, valid_emission_states = transitions[current_state], emissions[observation[next_index]]
            #need to make sure can handle unknown words
            if not valid_emission_states:
                valid_emission_states = emissions['<unk>']
            valid_to_states = set(valid_transitions) & set(valid_emission_states) #the intersection of the state keys
            state_heap = []
            for state in valid_to_states:
                trans_prob, emit_prob = math.log10(valid_transitions[state]), math.log10(valid_emission_states[state]) #make sure use logs to avoid underflow
                new_prob = prev_state_prob + trans_prob + emit_prob #they're logprobs, so adding
                next_state_predecessor = (current_state, new_prob) #basically the prob to get to here
                heappush(state_heap, (new_prob, state, next_state_predecessor)) #negative logprob to convert minheap to maxheap
                #update state table
                ########could move update state table so it happens when a node is popped of####### If it is being slow
                #update_state_table(state_table, next_state_predecessor, state, next_index + 1)
            while state_heap: #puts states into the deque with the lowest probability first. This is because I switched to a stack and DFS.
                best_state_prob, best_state, best_state_pred = heappop(state_heap)
                #append new states
                search_states.append((best_state, next_index+1, best_state_pred))

        else:
            winner = current_state
            winner_logprob = state_table[winner][end_of_input][1]
            win_sequence = backtrace(winner, end_of_input, final_sequence, state_table)
            win_sequence.reverse()
            return win_sequence, winner_logprob
    #print('No valid observed hidden sequences found')

def check_valid_prob(num, line_num):
    '''
    :param num: a number to be checked if a valid prob
    :param line_num:
    :return: Boolean. Prints warning to stderr if False.
    '''
    if num >= 0 and num <= 1:
        return True
    else:
        print('warning: the given prob is not in the [0,1] range on: Line {}. Line skipped.'.format(line_num), file=sys.stderr)
        return False

def backtrace(state, index, final_sequence, state_table): #traces back through the paths from state_table
    predecessor = state_table[state][index]
    prev_state = predecessor[0]
    final_sequence.append(state)
    if prev_state != '**': #symbol for predecessor of start
        backtrace(prev_state, index-1, final_sequence, state_table)
    return final_sequence

def read_hmm(inputfilename):
    '''
    Reads in an hmm of standard format into some dicts of initial states, transitions, emissions.
    NOTE that while this is very similar to an hmm validation checker, the emission are read differently and the dict
    keys are the emitted observations, rather than the states. This is because it makes viterbi easier.
    :param input: an hmm file of standard format
    :return: dicts of initial states, transitions, emissions
    '''
    header = defaultdict(float)
    initial_states, transitions, emissions = defaultdict(float), defaultdict(lambda: defaultdict(float)), \
                                             defaultdict(lambda: defaultdict(float))
    init, transition, emission = '\\init', '\\transition', '\\emission'
    init_line_num, trans_line_num, emit_line_num = 0, 0, 0
    failed_init_lines, failed_trans_lines, failed_emit_lines = 0, 0, 0
    all_states, all_sym = set(), set()

    with open(inputfilename, 'rU') as infile:
        line_num = 0
        for line in infile: #this reads in the header
            line_num += 1
            strip_line = line.strip()
            if strip_line:
                if strip_line == init:
                    break
                key, value = strip_line.split('=')
                header[key] = float(value)
        #start reading initial states
        #YES all of this shit is super redundant and needs to be put in functions sometime when I have more time.
        for line in infile:
            line_num += 1
            strip_line = line.strip()
            if strip_line:
                if strip_line == transition:
                    break
                tokens = strip_line.split()
                if len(tokens) > 1:
                    init_state, init_prob = tokens[0], float(tokens[1])
                    if check_valid_prob(init_prob, line_num):
                        initial_states[init_state] = init_prob
                        #this leaves off logprob, but that is fine, we can recalc later.
                        #it also doesn't currently check if you have multiple lines w same initial state but diff probs
                        #it just overwrites
                        init_line_num += 1
                        all_states.add(tokens[0])
                    else:
                        failed_init_lines += 1
                else:
                    print("Invalid Initial Probability line. Line is being skipped:\n{}"
                          .format(strip_line), file=sys.stderr)
                    failed_init_lines += 1
        #start reading transitions into a nested dict in form {from_state {to_state:prob}}
        for line in infile:
            line_num += 1
            strip_line = line.strip()
            if strip_line:
                if strip_line == emission:
                    break
                tokens = strip_line.split()
                if len(tokens) > 2:
                    from_state, to_state, prob = tokens[0], tokens[1], float(tokens[2]) #this leaves off logprob, but that is fine, we can recalc later.
                    if check_valid_prob(prob, line_num):
                        trans_line_num += 1
                        #add to set of all states
                        all_states.add(from_state)
                        all_states.add(to_state)
                        #add to transitions dict
                        if transitions[from_state]:
                            transitions[from_state][to_state] = prob
                        else:
                            transitions[from_state] = {to_state: prob}
                    else:
                        failed_trans_lines += 1
                else:
                    print("Invalid Transition Probability line. Line is being skipped:\n{}".format(strip_line))
                    failed_trans_lines += 1
        #start reading in emissions into dict of emission: {state: prob}
        for line in infile:
            line_num += 1
            strip_line = line.strip()
            if strip_line:
                tokens = strip_line.split()
                if len(tokens) > 2:
                    state, emission, prob = tokens[0], tokens[1], float(tokens[2])
                    emit_line_num += 1
                    all_sym.add(emission)
                    if emissions[emission]:
                        emissions[emission][state] = prob
                    else:
                        emissions[emission] = {state: prob}
                else:
                    print("Invalid Emission Probability line. Line is being skipped:\n{}".format(strip_line))
                    failed_trans_lines += 1
    return initial_states, transitions, emissions


if __name__ == "__main__":
    input_hmm, test_file_name, output_file_name = sys.argv[1], sys.argv[2], sys.argv[3]
    test_observation = "Absent other working capital , he said , the RTC would be forced to delay other thrift resolutions until cash could be raised by selling the bad assets .".split()
    #test_observation = "normal cold dizzy".split()
    initial_states, transitions, emissions = read_hmm(input_hmm)
    output_lines = []
    with open(test_file_name, 'rU') as infile:
        for line in infile:
            #print('Running Viterbi for line: {}'.format(line))
            test_observation = line.strip().split()
            result = viterbi(test_observation, initial_states, transitions, emissions)
            if result:
                output_sequence, output_prob = result
                new_output_line = '{} => {} {}\n'.format(line.strip(), ' '.join(output_sequence), output_prob)
            else:
                new_output_line = '{} => *NONE*\n'.format(line.strip())
            output_lines.append(new_output_line)
    with open(output_file_name,'w') as outfile:
        [outfile.write(output_line) for output_line in output_lines]


