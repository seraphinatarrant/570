'''
Command: ngram_count.py training_data ngram_count_file_name
Takes in training data and spits out ngram counts to the given filename

Assumes training data is tokenised, and is *one sentence per line*

Steps:
Read in sentences (batch or line by line)
Insert BOS <s> and EOS </s> at sentence boundaries

Collect ngrams from training data
Use a counter

Output:
unigrams, bigrams, trigrams
sort the lines by the frequency of ngrams in descending order


'''
import sys
from collections import Counter



def process_sentence(input):
    '''
    Read in sentences (batch or line by line)
    Insert BOS and EOS symbols at sentence boundaries
    :param input: a sentence string
    :return: processed sentence
    '''
    sentence = '<s> '+input.rstrip()+' </s>' #rstrip prevents the EOS from being appended after the newline
    return sentence

def count_ngrams(input, n=3):
    '''
    Collects ngrams from training data. Takes only one n, not a range, so if want unigram, bigram, trigram,
    then need to call multiple times and get a separate Counter object for each.
    :param input: an input list of sentence strings, pre-tokenised and with EOS and BOS appended
    :param n: the n of 'ngram' (ie unigram, bigram, etc)
    :return: a Counter of ngram counts. Defaults to trigram.
    '''
    ngram_counter = Counter()
    for sentence in input:
        tokens = sentence.split()
        index, end = 0, len(tokens)
        #add ngrams to counter
        while index+(n-1) < end:
            token = ' '.join([tokens[index+i] for i in range(0,n)]) #makes sure the token is the correct ngram
            ngram_counter[token] += 1
            index += 1 #steps forward in list
    return ngram_counter


def build_ngram_counts(inputfile, outputfile = 'tmp_ngram_output', ngrams = [1,2,3]):
    '''
    Master function that executes the steps of processing input, counting ngrams, and outputting file.
    :param inputfile: name of input file
    :param outputfile: name of output file
    :param ngrams: the ngrams to include. Defaults to a list of unigram, bigram, and trigram
    :return: None
    '''
    training_data = [] # important that this is a list not a set since we want to preserve duplicates

    #Preprocess the input with BOS and EOS symbols
    with open(inputfile,'rU') as infile:
        for line in infile:
            new_line = process_sentence(line)
            training_data.append(new_line)
    #Count ngrams
    with open(outputfile, 'w') as outfile:
        for number in ngrams:
            result = count_ngrams(training_data, number).most_common()
            [outfile.write(str(line[1])+' '+line[0]+'\n') for line in result]



if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    build_ngram_counts(input_file, output_file)



