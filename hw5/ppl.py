'''
Calculates perplexity of test data given an LM. Uses interpolation for smoothing.
Command: ppl.py lm_file lambda_1 lambda_2 lambda_3 test_data output_file (6 args total)

'''
import sys
import math
from collections import Counter, defaultdict


def calc_corpus_ppl(test_data, ngrams, l3, l2, l1, output_file = 'tmp_ppl_output'):
    #test data is the data to test on, ngrams is a defaultdict with ngram probabilities. Do I need to do anything with the absolute counts?
    input, output = open(test_data, 'rU'), open(output_file, 'w')
    total_prob, total_words, total_oov, sentence_num, current_sentence = 0, 0, 0, 0, 0
    for line in input:
        oov_num, sentence_prob, sentence_ppl = 0, 0, 0
        current_sentence += 1 #used for labelling output
        sent_with_markers = '<s> ' + line.rstrip() + ' </s>'
        output.write('Sent #{}: {}\n'.format(current_sentence, sent_with_markers)) #write the sentence before doing any processing
        sentence = sent_with_markers.split()
        num_words = len(sentence)-2  #Excludes the BOS and EOS symbols. Store this so don't have to recalculate later...even though the time it takes to calculate it tiny. But what if its Proust?!!!
        current_index = 1 #skip BOS symbol
        for word in sentence[1:]: #start iteration after BOS symbol
            flag = ''
            #grab bigrams and trigrams, mostly for output formatting later
            bigram = (sentence[current_index - 1], word)
            if current_index > 1:
                trigram = (sentence[current_index - 2], sentence[current_index - 1], word)
            else:
                trigram = bigram  # account for the fact that P(w|BOS BOS) == P(w|BOS)
            #if unigram exists in model data, calculate trigram probabilitiy
            unigram_prob = ngrams[(word,)]
            if unigram_prob:
                bigram_prob, trigram_prob = ngrams[bigram], ngrams[trigram]
                interpolated_prob = l3*trigram_prob + l2*bigram_prob + l1*unigram_prob
                log_prob = math.log10(interpolated_prob)
                sentence_prob += log_prob
                if bigram_prob == 0 or trigram_prob == 0:
                    flag = ' (unseen ngrams)'
            #if unigram doesn't exist, increment oov_num set prob -inf, etc
            else:
                oov_num += 1
                log_prob = '-inf'
                flag = ' (unknown word)'
            output.write('{}: lg P({} | {}) = {}{}\n'.format(current_index, word, ' '.join(trigram[:-1]), log_prob, flag))
            current_index += 1
        #once sentence is processed, increment totals
        total_oov += oov_num
        total_words += num_words
        total_prob += sentence_prob
        count = num_words + 1 - oov_num
        #calculate sentence ppl
        av_sentence_prob = -sentence_prob/count
        sentence_ppl = math.pow(10, av_sentence_prob)
        #write sentence specific info
        output.write('{} sentence, {} words, {} OOVs\n'.format(1, num_words, oov_num))
        output.write('lgprob={} ppl={}\n\n\n\n'.format(total_prob, sentence_ppl))
    #write corpus specific info
    av_prob = total_prob/(current_sentence+total_words-total_oov)
    ppl = math.pow(10, -av_prob)
    output.write('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n'
                 'sent_num={} word_num={} oov_num={}\n'
                 'lgprob={} ave_lgprob={} ppl={}\n'.format(current_sentence, total_words, total_oov, total_prob, av_prob, ppl))

def process_lm(in_file):
    '''
    read in an lm file and create a dictionary of probabilities
    :param lm_file: a language model file in ARPA format
    :return: a default dict of ngram: prob based on lm (language model)
    '''
    ngram_probs = defaultdict(float)
    section_titles = ['\\1-grams:', '\\2-grams:', '\\3-grams:']
    start_reading = False
    with open(in_file, 'rU') as lm_file:
        for line in lm_file:
            if line.strip() in section_titles:
                start_reading = True
            if start_reading:
                data = line.strip().split()
                if len(data) > 3:
                    prob, ngram = float(data[1]), tuple(data[3:])
                    ngram_probs[ngram] = prob
    return ngram_probs

if __name__ == "__main__":
    lm_file, test_data = sys.argv[1], sys.argv[5]
    lambda1, lambda2, lambda3 = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
    #output_file = sys.argv[6]
    lm_ngram_probs = process_lm(lm_file)
    #print(lm_ngram_probs[('Pierre',)])
    corpus_ppl = calc_corpus_ppl(test_data, lm_ngram_probs, lambda3, lambda2, lambda1)