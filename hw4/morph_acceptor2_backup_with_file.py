#checks whether input words are accepted by the given expanded FSM (of type created in Q1)
#command morph_acceptor.py fsm word_list
'''
wordlist is a list of words, one per line
output file has format "input word => answer" where answer is either morph1/label1 morph2/label2 or *NON*


'''
import subprocess
import sys
import re

if __name__ == "__main__":
    fsm = sys.argv[1]
    input_file = sys.argv[2]
    line_dict = {}
    line_list = []
    temp_file = 'temp_file'

    with open(input_file,'rU') as file:
        for line in file:
            if line:
                new_line = re.sub(r'(.)', r'\1 ', line).strip()
                #line_dict[line.strip()] = new_line
                line_list.append(new_line)
    with open(temp_file,'w') as file:
        for line in line_list:
            file.write(line+'\n')
    #for item in line_dict.items():
        #print('Input {} Modified Input {}'.format(item[0],item[1]))

    output = subprocess.check_output('cat {}|carmel {} -slibOE'.format(temp_file, fsm), shell=True, universal_newlines=True, stderr=subprocess.STDOUT).split('\n')
    current_index = 0
    for line in output:
        print(line)
        '''
        input_string=re.search('(?<=Input line \d:).*', line)
        if input_string:
            next_line = output[current_index+1]
            if '(0 states / 0 arcs)' in next_line:
                result = 'no'
            else:
                result = 'yes'
            print(input+' => '+result)
        current_index+=1
'''