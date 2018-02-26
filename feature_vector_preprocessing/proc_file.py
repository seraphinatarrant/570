'''
A script that generates feature vectors from an input file.
Command to run: proc_file.py input_file targetLabel output_file

input file:
textfile of particular format
output file:
instanceName targetLabel f1 v1 f2 v2 where instanceName is input filename, and targetLabel is given from commandline

skip header (all text before first blankline)
replaceall chars not [a-zA-Z] with whitespace and lowercase all chars
tokenise by whitespace
words are features, values or the freq in file of that word
featname, val pairs are ordered by featname spelling
'''

import sys
from collections import Counter

import re


def process_file(input_filename):
    '''
    A function that takes and input file and returns a counter of word freq pairs
    :param input_filename: an input file of standard format (basically with a header to be skipped)
    :param non_alpha: the regex to substitute with whitespace before tokenisation
    :param output_filename:
    :return: Counter of word freq pairs
    '''
    word_freq = Counter()
    non_alpha = re.compile('[^A-Za-z]+')
    with open(input_filename, 'rU') as infile:
        start_reading = False
        for line in infile:
            # skip header
            line = line.strip()
            if start_reading:
                line = non_alpha.sub(' ', line)
                word_tokens = line.lower().split()
                #once have a list of word tokens, add them to a counter
                for token in word_tokens:
                    if word_freq[token]:
                        word_freq[token] += 1
                    else:
                        word_freq[token] = 1
            else:
                if not line:
                    start_reading = True
    return word_freq

def main(input_filename, target_label, output_filename):
    '''
    :param input_filename: name of textfile of particular format
    :param target_label: the class label of the feature vector set
    :param output_filename: the filename to write to
    :return: none - writes file
    '''

    feature_vector_data = process_file(input_filename)
    feature_vlist = ' '.join(["{} {}".format(key, val) for key, val in sorted(feature_vector_data.items())])
    output_data = "{} {} {}".format(input_filename, target_label, feature_vlist)
    with open(output_filename, 'w') as outfile:
        outfile.write(output_data)

if __name__ == "__main__":
    input_filename, target_label, output_filename = sys.argv[1], sys.argv[2], sys.argv[3]
    main(input_filename, target_label, output_filename)



    