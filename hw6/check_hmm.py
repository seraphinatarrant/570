'''
A script that reads in an hmm file and outputs warnings based on whether the header matches the file contents and
whether the three kinds of constraints for an HMM are met.

Command to run: check_hmm.py input_hmm > warning_file

Prints out header (or warnings) either way.
Warnings in order of warnings regarding header.


Another of my solutions has been to force all states ending in an EOS tag to transition to an EOS sink (EOS_EOS) with probability=1.0.

For example:

transition probability(DT_EOS, EOS_EOS) = 1.0

transition probability(DT_EOS, anything else) = 0.0

transition probability(EOS_EOS, EOS_EOS) = 1.0

This ensures that every state (including EOS_EOS) has trans_prob_sum=1, and also ensures that the EOS sinks behave like true sinks. Trying to transition from EOS to any other non-EOS state is inherently flawed since the training data, by definition, cannot include any EOS-->[other tag] ngrams.

Q5) I have to assume we write all P(<unk> | tag) probabilities to output, otherwise we can't sum all emission probabilities to 1.




'''

import sys
import math
from collections import Counter, defaultdict, OrderedDict

from numpy import array, zeros

def read_hmm(input):
    header = OrderedDict()
    initial_states, transitions, emissions = defaultdict(float), defaultdict(lambda: defaultdict(float)), \
                                             defaultdict(lambda: defaultdict(float))
    start_reading_hmm = False
    init, transition, emission = '\\init', '\\transition', '\\emission'
    init_line_num, trans_line_num, emit_line_num = 0, 0, 0
    failed_init_lines, failed_trans_lines, failed_emit_lines = 0, 0, 0
    all_states = set()

    with open(input, 'rU') as infile:
        for line in infile: #this reads in the header
            strip_line = line.strip()
            if strip_line:
                if strip_line == init:
                    start_reading_hmm = True
                if start_reading_hmm:
                    break
                key, value = strip_line.split('=')
                header[key] = float(value)
        #start reading initial states
        #YES all of this shit is super redundant and needs to be put in functions sometime when I have more time.
        for line in infile:
            strip_line = line.strip()
            if strip_line:
                if strip_line == transition:
                    break
                tokens = strip_line.split()
                if len(tokens) > 1:
                    initial_states[tokens[0]] = float(tokens[1]) #this leaves off logprob, but that is fine, we can recalc later.
                    #it also doesn't currently check if you have multiple lines with same initial state and different probs
                    #it just overwrites
                    init_line_num += 1
                    all_states.add(tokens[0])
                else:
                    print("Invalid Initial Probability line. Line is being skipped:\n{}".format(strip_line))
                    failed_init_lines += 1
        #start reading transitions into a nested dict
        for line in infile:
            strip_line = line.strip()
            if strip_line:
                if strip_line == emission:
                    break
                tokens = strip_line.split()
                if len(tokens) > 2:
                    from_state, to_state, prob = tokens[0], tokens[1], float(tokens[2]) #this leaves off logprob, but that is fine, we can recalc later.
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
                    print("Invalid Transition Probability line. Line is being skipped:\n{}".format(strip_line))
                    failed_trans_lines += 1
        #start reading in emissions into dict of emission: {state: prob}
        for line in infile:
            strip_line = line.strip()
            if strip_line:
                tokens = strip_line.split()
                if len(tokens) > 2:
                    state, emission, prob = tokens[0], tokens[1], float(tokens[2])
                    emit_line_num += 1
                    if emissions[emission]:
                        emissions[emission][state] = prob
                    else:
                        emissions[emission] = {state: prob}
                else:
                    print("Invalid Emission Probability line. Line is being skipped:\n{}".format(strip_line))
                    failed_trans_lines += 1
        #start printing out header or checks
        found_sym = len(set(emissions.keys()))
        found_states = len(all_states)
        header_template = '{}={}\n'
        #warning templates
        diff_numbers = 'warning: different numbers of {}: claimed={}, real={}\n'
        dont_sum_1 = 'warning: the {} for state {} is {}\n'
        #order is state, sym, init, trans, emit
        diff_states, diff_sym = header['state_num']-found_states, header['sym_num']-found_sym
        diff_init = header['init_line_num']-init_line_num
        diff_trans, diff_emit = header['trans_line_num']-trans_line_num, header['emiss_line_num']-emit_line_num
        #this organisation allows me to decide to print what failed if it seems helpful
        if diff_states == 0:
            states_line = header_template.format('state_num',found_states)
        else:
            states_line = diff_numbers.format('state_num', header['state_num'], found_states)
        if diff_sym == 0:
            sym_line = header_template.format('sym_num',found_sym)
        else:
            sym_line = diff_numbers.format('sym_num', header['sym_num'], found_sym)
        if diff_init == 0:
            init_line = header_template.format('init_line_num', init_line_num)
        else:
            init_line = diff_numbers.format('init_line_num', header['init_line_num'], init_line_num)
        if diff_trans == 0:
            trans_line = header_template.format('trans_line_num',trans_line_num)
        else:
            trans_line = diff_numbers.format('trans_line_num', header['trans_line_num'], trans_line_num)
        if diff_emit == 0:
            emit_line = header_template.format('emiss_line_num', emit_line_num)
        else:
            emit_line = diff_numbers.format('emiss_line_num', header['emiss_line_num'], emit_line_num)


        output = ("{}"
                  "{}"
                  "{}"
                  "{}"
                  "{}").format(states_line, sym_line, init_line, trans_line, emit_line)
        print(output)

        #print(emissions)
        #print(initial_states)
        #print(transitions)
        #print(emissions)

def read_lines(min_tokens, stop_reading):
    pass






if __name__ == "__main__":
    input = sys.argv[1]
    read_hmm(input)


'''
 #initialise arrays and give some padding to the max size in case of errors in header
        init_lines = math.ceil(header['init_line_num']*1.05)
        trans_lines, emit_lines = math.ceil(header['trans_line_num']*1.05), math.ceil(header['emiss_line_num']*1.05)
        state_num, symbol_num = math.ceil(header['state_num']*1.05), math.ceil(header['sym_num']*1.05)
        #make arrays: 1D for inits and 2D for trans and emit
        init_probs, trans_probs, emit_probs = zeros((init_lines)), \
                                              zeros((trans_lines, trans_lines)), zeros((emit_lines, emit_lines))
        #make dicts
        state2index, symbol2index = Counter(), Counter()
        indextostate, index2symbol = zeros((state_num)), zeros((symbol_num))
        state2index_counter, symbol2index_counter = 0,0

        #this reads in the init lines
        for line in infile:
            strip_line = line.strip()
            if strip_line:
                if strip_line == transition:
                    break
                tokens = strip_line.split()
                #for init lines there should be 2 or 3 tokens
                state2index[tokens[0]] = state2index_counter
                state2index_counter += 1


'''