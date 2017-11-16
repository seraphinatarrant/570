'''
A script that converts the output of an hmm POS tagger into annotated training data.
Command to run: cat file1 | conv_format.py > file2

file1 format: obvservation => state_seq logprob.
file2 format: w1/t1 w2/t2...wn/tn where t_i is the second tag in the state sequence for w_i.
'''

import sys

def format_obs_state_pairs(inputline_list):
    #might want to consider doing this line by line
    output_lines = []
    for line in inputline_list:
        obs, states = line.split('=>') #split observation and state sequence on the character delimiting them
        #the [:-1] below is cause the final entry will be logprob rather than a statename which we dont want to capture
        #starting states from 1 ensures it doesn't capture BOS_BOS
        obs_tokens, states_tokens = obs.split(), states.split()[1:-1]
        #need to convert the list of states to a list of tags, which is the second tag in the state name
        tags = [state.split('_')[1] for state in states_tokens]
        zipped_tokens = zip(obs_tokens, tags)
        output_tokens = []
        [output_tokens.append('{}/{}'.format(pair[0], pair[1])) for pair in zipped_tokens]
        output_lines.append('{}'.format(' '.join(output_tokens))) #if change to write to a file will want to put \n here
    for line in output_lines:
        print(line)




if __name__ == "__main__":
    #input_filename = sys.argv[1] #this will be removed for the cat pipe but is here for debugging
    input_data = sys.stdin.readlines()
    inputlines = []

    #with open(input_filename, 'rU') as infile:
    #    for line in infile:
    #        if line:
    #            inputlines.append(line.strip())
    for line in input_data:
        if line:
            inputlines.append(line.strip())
    format_obs_state_pairs(inputlines)
    