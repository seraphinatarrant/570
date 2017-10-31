'''
Calculates perplexity of test data given an LM. Uses interpolation for smoothing.
Command: ppl.py lm_file lambda_1 lambda_2 lambda_3 test_data output_file (6 args total)

'''

def calc_ppl(test_data,lm):
    total_prob, total_words, oov_num, sentence_num = 0, 0, 0, 0
    for sentence in test_data:
        total_words += NUM_WORDS_EXCL_BOS_EOS
        for word in sentence:
            if unigram exists:
                CALC_PPL



if __name__ == "__main__":
    lm, lambda1, lambda2, lambda3, test_data = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
    output_file = sys.argv[6]
