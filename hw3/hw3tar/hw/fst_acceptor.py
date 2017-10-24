import subprocess
import sys
import re

if __name__ == "__main__":
    fst = sys.argv[1]
    input_file = sys.argv[2]

    output = subprocess.check_output('cat {}|carmel {} -slib'.format(input_file,fst),shell=True, universal_newlines=True,stderr=subprocess.STDOUT).split('\n')

    current_index = 0
    for line in output:
        #print("???",line)
        #result = None
        prob = 1
        input_string=re.search('(?<=Input line \d:).*', line)
        if input_string:
            input = input_string.group(0)
            next_line = output[current_index+1]
            #print('***',next_line)
            if '(0 states / 0 arcs)' in next_line:
                result = '*none*'
                prob = 0
            else:
                next_line = output[current_index+2]
                #print(next_line)
                result = ' '.join([item.strip() for item in re.findall('(?<=:)\s"?[\w\*]*"?\s', next_line)]) #capture everything on the output line between a colon and a slash..or space since one character at a time
                #prob_list = [float(item.strip()) for item in re.findall('(?<=[/])\s[\w\.]+', next_line)]#product of all the numbers after the slashes before parens
                #for num in prob_list:
                    #prob *= num
                #I JUST NOW realised that carmel gives you the probability...so this grabs it rather than me calculating it
                prob = ''.join(re.findall('(?<= )[\d\.]+$', next_line))
            print(input+' => '+result,prob)
        current_index+=1


'''
output to process
???     (3 states / 2 arcs)
??? (0 -> 0 "a" : "b" / 1) (1 -> 1 "a" : "b" / 1) 1
???     (3 states / 2 arcs)
??? (0 -> 0 "a" : *e* / 1) (1 -> 1 "a" : "b" / 1) 1

output format: input => output prob


CAN CHANGE TO -slibOE to get this format:
Input line 2: "C" "S" "B" "B" "Z"
        (6 states / 6 arcs)
"A" "E" "T" "C" "M" 0.626282389512024


'''
