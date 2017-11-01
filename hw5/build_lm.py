'''
Builds a language model using ngram counts
Command: build_lm.py ngram_count_file lm_file
ngram_count file is in format produced in ngram_count.py
lm_file is output, in the modified ARPA format
No smoothing used - so we do not output any information on unseen ngrams
'''

import math
import sys
from collections import Counter, defaultdict

'''
get num unique unigrams (types)
get num unique bigrams
get num unique trigrams
'''
def build_lm(input_file, output_file = 'tmp_lm_output'):
    '''
    Counters of (ngram tuple) : count
    :param input_file:
    :return:
    '''
    unigrams = Counter()
    bigrams = Counter()
    trigrams = Counter()
    ngram_probs = defaultdict(float)
    ngram_counters = [unigrams, bigrams, trigrams]
    with open(input_file, 'rU') as infile:
        for line in infile:
            line_pieces = line.split()
            n = len(line_pieces)-1
            count, ngram = int(line_pieces[0]), tuple(line_pieces[1:])
            if n == 1:
                unigrams[ngram] = count
            elif n == 2:
                bigrams[ngram] = count
            elif n == 3:
                trigrams[ngram] = count

    with open(output_file, 'w') as outfile:
        #write data section and build probability dicts
        outfile.write('\\data\\\n')
        ngram_type = 1 #since start with unigrams (basically this is just formatting of how ARPA is)
        all_grams = unigrams + bigrams + trigrams
        for ngram_counter in ngram_counters:
            types, tokens = len(ngram_counter.keys()), sum(ngram_counter.values())
            outfile.write('ngram {}: type={} token={}\n'.format(ngram_type, types, tokens)) #write the /data/ section

            for key in ngram_counter: #populate dict of probabilities for each ngram key in Counter dict
                count = ngram_counter[key]
                if ngram_type == 1:
                    divisor = tokens #if unigram, divide by num tokens
                else:
                    divisor = all_grams[key[:-1]] #else divide by the n-1 gram
                prob = count/divisor
                logprob = math.log(prob, 10)
                ngram_probs[key] = (prob, logprob)
            ngram_type += 1

        #write ngram sections
        ngram_type = 1
        for ngram_counter in ngram_counters:
            #types, tokens = len(ngram_counter.keys()), sum(ngram_counter.values())
            outfile.write('\n\\{}-grams:\n'.format(ngram_type))
            for entry in ngram_counter.most_common():
                key = entry[0]
                outfile.write('{} {} {} {}\n'.format(ngram_counter[key], ngram_probs[key][0], ngram_probs[key][1], ' '.join(key)))
            ngram_type += 1



if __name__ == "__main__":
    input_file, output_file = sys.argv[1], sys.argv[2]
    build_lm(input_file, output_file)
