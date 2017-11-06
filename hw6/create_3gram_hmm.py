'''
A script that takes annotated training data and creates a state-emission HMM for a TRIGRAM POS tagger,
where output symbols are generated by the to-states. Smoothing with interpolation.
Command to run: cat training_data | create_3gram_hmm.py output_hmm_file l1 l2 l3 unk_prob_file
(5 args, not including the input)
(Yes it is weird to use cat, it was a requirement for some reason)

unk_prob_file is P(unknown word|tag) and is in format 'tag prob', and is used for smoothing to give some probability
mass to unknown words.

States: each is now a tag PAIR. Each state remembers the current and the previous state.
This takes the HMM limitation that each state depends on only the previous one and adapts for trigrams.
Output: Same as a bigram hmm - words, and BOS, EOS symbols
Init prob: BOS_BOS 1.0
Transition prob: a_ij = P(s_j|s_i) = P(t_3|t_1, t_2) where s_i = (t_1,t_2) and s_j = (t_2',t_3) and t_2 == t_2'.
Where t_2 != t_2' Prob will be 0.
Emission prob: b_jk = P(w_k|s_j) where s_j = (t1,t2) = P(w_k|t2) for any t1

Therefore:
Transition probabilities between states are trigram probabilities, where states are bigrams that must
"overlap" by the edges of their bigrams.
Emission probabilities from the to state are the bigram probability of the word given the second tag in the to_state.

All probabilities are adjusted with smoothing.
Emission probabilities are adjusted so that:
Known words: Psmooth(w|tag) = P(w|tag) * (1 - P(<unk>|tag))
Unknown words: Psmooth(w|tag) = P(<unk>|tag)

'''

import sys
from collections import Counter, defaultdict

import re

import math


def process_sentence(input, regex):
    '''
    Read in sentences (batch or line by line)
    Insert BOS and EOS symbols and tags at sentence boundaries, split on whitespace, convert to word, tag tuples
    :param input: a sentence string
    :return: list of tuples of (word, tag) from processed sentence
    '''
    sentence_tuples = [('<s>', 'BOS')]
    #sentence = input.strip().split()
    sentence_tuples.extend([tuple(regex.split(token, 1)) for token in input.strip().split()])
    sentence_tuples.append(('<\/s>', 'EOS'))
    return sentence_tuples

def count_ngrams(input, n=2):
    '''
    Collects ngrams from input (splodged together from a more general ngram counter, hence why there is an n param)
    NOTE that I reverse the word_tag_bigram tuples to be tag_word bigram tuples for easier handling
    :param input: a list of sentence-lists of (word, tag) tuples
    :param n: the n of 'ngram' (eg unigram, bigram). Default  2. Wouldn't actually work with anything else at present.
    :return: counters of tag unigram, word unigram, tag word bigram,  and tag bigram
    '''
    tag_unigrams, tag_bigrams, word_unigrams, tag_word_bigrams = Counter(), Counter(), Counter(), Counter()
    for sentence in input:
        index, end = 0, len(sentence)
        #add ngrams to counter
        while index < end:
            tag_word_bigram = tuple(reversed(sentence[index])) #this is so the format is tag,word so I can treat it like a normal bigram probability
            tag_unigram, word_unigram = tag_word_bigram[0], tag_word_bigram[1]

            tag_unigrams[tag_unigram] += 1
            word_unigrams[word_unigram] += 1
            tag_word_bigrams[tag_word_bigram] += 1
            if index+(n-1) < end:
                tag_bigram = (tag_unigram, sentence[index + 1][1])
                tag_bigrams[tag_bigram] += 1
            index += 1 #steps forward in list
    return tag_unigrams, tag_bigrams, word_unigrams, tag_word_bigrams

def calc_bigram_probs(bigrams, unigrams):
    '''
    :param bigrams: a Counter of bigram tuples
    :param unigrams: a Counter of unigram strings
    :return: a defaultdict of bigram probabilities
    '''
    prob_dict = defaultdict(float)
    for key in bigrams:
        prob = bigrams[key]/unigrams[key[0]]
        log_prob = math.log10(prob)
        prob_dict[key] = (prob, log_prob)
    return prob_dict

def make_hmm(data, output_file='tmp_hmm'):
    #assume data is preprocessed
    tag_unigrams, tag_bigrams, word_unigrams, tag_word_bigrams = count_ngrams(data)
    state_num, sym_num = len(tag_unigrams), len(word_unigrams)

    #calc emission and tranition probs from unigram and bigram counters
    transitions = calc_bigram_probs(tag_bigrams, tag_unigrams)
    emissions = calc_bigram_probs(tag_word_bigrams, tag_unigrams)
    init_line_num, trans_line_num, emiss_line_num = 1, len(transitions), len(emissions)

    #format data
    init_lines = "BOS 1.0 {}".format(math.log10(1))
    transition_lines = ['{} {} {} {}'.format(bigram_prob[0][0], bigram_prob[0][1], bigram_prob[1][0],
                                             bigram_prob[1][1]) for bigram_prob in transitions.items()]
    emission_lines = ['{} {} {} {}'.format(bigram_prob[0][0], bigram_prob[0][1], bigram_prob[1][0],
                                             bigram_prob[1][1]) for bigram_prob in emissions.items()]

    output = ("state_num={}\n"
              "sym_num={}\n"
              "init_line_num={}\n"
              "trans_line_num={}\n"
              "emiss_line_num={}\n\n"
              "\\init\n"
              "{init_lines}\n\n\n\n"
              "\\transition\n"
              "{transition_lines}\n\n"
              "\\emission\n"
              "{emission_lines}\n").format(state_num, sym_num, init_line_num, trans_line_num, emiss_line_num,
                                           init_lines=init_lines, transition_lines='\n'.join(transition_lines),
                                           emission_lines='\n'.join(emission_lines))
    with open(output_file,'w') as outfile:
        outfile.write(output)



if __name__ == "__main__":
    #output_filename = sys.argv[1]
    input = sys.argv[1]
    #input = sys.stdin.readlines() #this is how it will actually be executed
    inputlines = []
    regex_obj = re.compile(r'(?<!=\\)/')
    with open(input, 'rU') as infile:
        for line in infile:
            inputlines.append(process_sentence(line, regex_obj))

    make_hmm(inputlines)