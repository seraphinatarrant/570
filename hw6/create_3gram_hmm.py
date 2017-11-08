'''
A script that takes annotated training data and creates a state-emission HMM for a TRIGRAM POS tagger,
where output symbols are generated by the to-states. Smoothing with interpolation.
Command to run: cat training_data | create_3gram_hmm.py output_hmm_file l1 l2 l3 unk_prob_file
(5 args, not including the input)
(Yes it is weird to use cat, it was a requirement for some reason)

unk_prob_file is P(unknown word|tag) and is in format 'tag prob', and is used for smoothing to give some probability
mass to unknown words.

States: each is now a tag PAIR (bigram). Each state remembers the current and the previous state.
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

Interpolated trigram probability for t_3 (which will then be the transition probability) is:
P_1 = t_3/total_tag_tokens
P_2 = (t2,t3)/t2
P_3 = (t1,t2,t3)/(t1,t2)

All probabilities are adjusted with smoothing.
Emission probabilities are adjusted so that:
Known words: Psmooth(w|tag) = P(w|tag) * (1 - P(<unk>|tag))
Unknown words: Psmooth(w|tag) = P(<unk>|tag)

For interpolating with trigrams with unknown bigrams, that is:
val of P3(t_3|t_1, t_2) when (t_1, t_2) is unseen is undefined (divide by zero).
We cannot just set it to zero because Pinterpolated is only a distribution is P3, P2 and P1 all are.
So for the sake of simplicity when (t_1, t_2) is unseen:
P3(t_3|t_1, t_2) = 1/(T+1) where T is the size of the POS tagset (excl. BOS and EOS, hence the +1 to add EOS back)
except that when t_3 is BOS, set trigram prob to 0.

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

def count_ngrams(input):
    '''
    Collects POS type ngrams from input
    NOTE that I reverse the word_tag_bigram tuples to be tag_word bigram tuples for easier handling
    :param input: a list of sentence-lists of (word, tag) tuples
    :return: counters of tag unigram, tag bigram, tag trigram, word unigram, tag word bigram. keys all tuples
    '''
    tag_unigrams, tag_bigrams, tag_trigrams = Counter(), Counter(), Counter()
    word_unigrams, tag_word_bigrams = Counter(), Counter()
    for sentence in input:
        index, end = 0, len(sentence)
        #add ngrams to counter
        while index < end:
            tag_word_bigram = tuple(reversed(sentence[index])) #this is so the format is tag,word so I can treat it like a normal bigram probability
            tag_unigram, word_unigram = (tag_word_bigram[0], ), (tag_word_bigram[1], )

            tag_unigrams[tag_unigram] += 1
            word_unigrams[word_unigram] += 1
            tag_word_bigrams[tag_word_bigram] += 1
            if index+1 < end:
                tag_bigram = (tag_unigram[0], sentence[index+1][1])
                tag_bigrams[tag_bigram] += 1
                if index+2 < end:
                    tag_trigram = (tag_unigram[0], sentence[index+1][1], sentence[index+2][1])
                    tag_trigrams[tag_trigram] += 1
            index += 1 #steps forward in list
    return tag_unigrams, tag_bigrams, tag_trigrams, word_unigrams, tag_word_bigrams

def calc_word_probs(bigrams, unigrams, unk_prob_dict):
    '''
    With smoothing based on given P(<unk>|tag)
    Known words: Psmooth(w|tag) = P(w|tag) * (1 - P(<unk>|tag))
    :param bigrams: a Counter of bigram tuples, of form (tag, word)
    :param unigrams: a Counter of unigram tuples of form (tag, )
    :param unk_prob_dict: a defaultdict(float) of {tag:prob) where prob is P(<unk>|tag)
    :return: a defaultdict of bigram probabilities
    '''
    prob_dict = defaultdict(float)
    for key in bigrams:
        prob, unk_prob = bigrams[key]/unigrams[(key[0],)], unk_prob_dict[key[0]]
        smooth_prob = prob*(1-unk_prob)
        log_prob = math.log10(smooth_prob)
        prob_dict[key] = (smooth_prob, log_prob)
    return prob_dict

def calc_ngram_probs(ngrams, uni_tokens):
    '''
    Note that I do not calc logprob here since I need only normal probs as this will be used for interpolation.
    Also having tuple rather than floats would ruin the way the defaultdict returns 0 when Key is missing.
    :param ngrams: a Counter of ngrams and counts
    :param uni_tokens: total unigram tokens (to get unigram probabilities)
    :return: a probability dict of ngrams and their probabilities
    '''
    prob_dict = defaultdict(float)
    for key in ngrams:  # populate dict of probabilities for each ngram key in Counter dict
        count = ngrams[key]
        if len(key) == 1:
            divisor = uni_tokens  # if unigram, divide by num tokens
        else:
            divisor = ngrams[key[:-1]]  # else divide by the n-1 gram
        prob = count / divisor
        #logprob = math.log10(prob)
        prob_dict[key] = prob
    return prob_dict

def calc_interpolated_probs(states, prob_dict, tag_types):
    interpolated_prob_dict = defaultdict(float)
    for state_i in states:
        for state_j in states:
            if state_i[1] != state_j[0]:
                continue
            elif state_i == state_j:
                continue
            else: #prob state_i to state_j
                tag3, tag2, tag1 = state_j[1], state_i[1], state_i[0]
                unigram_prob, bigram_prob = prob_dict[(tag3,)], prob_dict[(tag2, tag3)]
                if bigram_prob:
                    trigram_prob = prob_dict[(tag1, tag2, tag3)]
                else:
                    trigram_prob = 1/(tag_types-1)
                interpolated_prob = l3*trigram_prob + l2*bigram_prob + l1*unigram_prob
                interpolated_log = math.log10(interpolated_prob)
                state_label_i, state_label_j = '{}_{}'.format(state_i[0], state_i[1]), '{}_{}'.format(state_j[0], state_j[1])
                interpolated_prob_dict[(state_label_i, state_label_j)] = (interpolated_prob, interpolated_log)
    return interpolated_prob_dict

def find_all_states(unigrams):
    '''
    :param unigrams: a dictionary of the unigrams from which to generate all possible bigrams (which are the state
    labels in a trigram hmm)
    :return: a set of all state labels in bigram tuple form
    '''
    state_set = set()
    for tag_i in unigrams:
        for tag_j in unigrams:
            new_tag = (tag_i[0], tag_j[0]) #making a bigram tuple out of that unigram tags (have to index them as the unigrams are tuples)
            state_set.add(new_tag)
    return state_set

def make_hmm(data, unk_prob_dict, lambda1, lambda2, lambda3, output_file='tmp_hmm_trigram'):
    #assume data is preprocessed
    tag_unigrams, tag_bigrams, tag_trigrams, word_unigrams, tag_word_bigrams = count_ngrams(data)
    state_num, sym_num = len(tag_bigrams), len(word_unigrams) #since now the states are bigrams
    all_states = find_all_states(tag_unigrams)
    tag_tokens, tag_types = sum(tag_unigrams.values()), len(tag_unigrams)


    #calc tag probs and word probs and use tag probs to calc interpolated trigram probs (which are transitions)
    tag_probs = calc_ngram_probs(tag_unigrams+tag_bigrams+tag_trigrams, tag_tokens)
    emission_probs = calc_word_probs(tag_word_bigrams, tag_unigrams, unk_prob_dict)
    transition_probs = calc_interpolated_probs(all_states, tag_probs, tag_types)

    init_line_num, trans_line_num, emiss_line_num = 1, len(transition_probs), len(emission_probs)
    
    #format data
    init_lines = "BOS_BOS 1.0 {}".format(math.log10(1))
    transition_lines = ['{} {} {} {}'.format(state_trans[0][0], state_trans[0][1], state_trans[1][0],
                                             state_trans[1][1]) for state_trans in transition_probs.items()]
    emission_lines = ['{} {} {} {}'.format(emission[0][0], emission[0][1], emission[1][0],
                                             emission[1][1]) for emission in emission_probs.items()]
    (print(tag_types))
    (print(len(all_states)))
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



def read_probs(prob_file):
    prob_dict = defaultdict(float)
    with open(prob_file, 'rU') as infile:
        for line in infile:
            if line:
                tag, prob = line.strip().split()
                prob_dict[tag] = float(prob)
    return prob_dict



if __name__ == "__main__":
    #output_filename = sys.argv[1]
    input = sys.argv[1]
    l1, l2, l3 = [float(num) for num in [sys.argv[2], sys.argv[3], sys.argv[4]]]
    unk_prob_file = sys.argv[5]
    #input = sys.stdin.readlines() #this is how it will actually be executed
    inputlines = []
    regex_obj = re.compile(r'(?<!\\)/')

    with open(input, 'rU') as infile:
        for line in infile:
            inputlines.append(process_sentence(line, regex_obj))

    #read in unk_prob_file
    unk_prob_dict = read_probs(unk_prob_file)

    make_hmm(inputlines, unk_prob_dict, l1, l2, l3)
