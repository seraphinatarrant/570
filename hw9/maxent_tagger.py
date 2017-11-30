'''
A script that will
1. Create feature vectors for the training data and the test data. The vector files should be called
final train.vectors.txt and final test.vectors.txt.
2. Run mallet import-file to convert the training vectors into binary format, and the binary file
is called final train.vectors.
3. Run mallet train-classifier to create a MaxEnt model me model using final train.vectors
4. Run mallet classify-file to get the result on the test data final test.vectors.txt.
5. Calculate the test accuracy

Command to run: maxent tagger.py train_file test_file rare_thres feat_thres output_dir

1. create train_voc from the train_file, and use the word frequency in train_voc and rare_thres to
determine whether a word should be treated as a rare word. This changes the feature vectors.

2. Form feature vectors for the words in train_file, and store the features and frequencies in the
training data in init_feats. In this case, features are taken from Ratnaparkhi ~1996, and vector values are binary OR
the string itself.

3. Prune features from init_feats based on feat_thres. NOTE that w_i feats are NOT pruned, only others.

4. Go through the feature vector file for train_file and REMOVE all the features that are not in
kept_feats.




'''
import sys
import re
from collections import Counter, defaultdict

import os
import subprocess


def process_sentence(input, regex):
    '''
    Read in sentences (batch or line by line)
    Insert BOS and EOS symbols and tags at sentence boundaries, split on whitespace, convert to word, tag tuples
    :param input: a sentence string
    :return: list of tuples of (word, tag) from processed sentence
    '''
    sentence_tuples = []
    sentence_tuples.extend([('BOS', 'BOS'), ('BOS', 'BOS')])
    #sentence = input.strip().split()
    sentence_tuples.extend([tuple(regex.split(token, 1)) for token in input.strip().split()])
    sentence_tuples.extend([('EOS', 'EOS'), ('EOS', 'EOS')])
    return sentence_tuples

def make_voc(word_list):
    '''
    takes an input wordlist and makes a vocabulary
    :return: Counter dictionary of words and frequencies
    '''
    # dict to store tokens
    voc_dict = Counter()
    # read input
    for word in word_list:
        if voc_dict[word]:
            voc_dict[word] += 1
        else:
            voc_dict[word] = 1
    del voc_dict['BOS']
    del voc_dict['EOS']
    return voc_dict

def generate_feature_vectors(input_sentences, voc_dict, rare_thres):
    #generates feature vectors for a single sentence
    #word_label_features is a defaultdict of with key (index, word_label pair) and set of feature vectors
    #for all words: t_i-1, (t_i-2, t_i-1), w_i-1, w_i-2, w_i+1, w_i+2
    #for non rare words: w_i
    #for rare words: w_i has prefix X, w_i has suffix X, both where X <= 4
    #w_i contains number, w_i contains uppercase, w_i contains hyphen

    word_label_features = defaultdict(set)
    feature_vecs = Counter()

    for sentence_index in range(len(input_sentences)):
        sentence = input_sentences[sentence_index]
        for word_tag_i in range(2, len(sentence)-2):
            features = []
            #grab features for all words
            prevW, prevT = 'prevW={}'.format(sentence[word_tag_i-1][0]), 'prevT={}'.format(sentence[word_tag_i-1][1])
            prev2W = 'prev2W={}'.format(sentence[word_tag_i-2][0])
            prevTwoTags = 'prevTwoTags={}+{}'.format(sentence[word_tag_i-2][1], sentence[word_tag_i-1][1])
            nextW, next2W =  'nextW={}'.format(sentence[word_tag_i+1][0]), 'next2W={}'.format(sentence[word_tag_i+2][0])
            #add features to list:
            features.extend([prevW, prevT, prev2W, prevTwoTags, nextW, next2W])

            curW, curT = sentence[word_tag_i]
            # grab features for rare words, if word is rare
            if voc_dict[curW] < rare_thres:
                if curW[0].isupper():
                    features.append('containUC')
                if re.search(r'\d', curW): #if no digits, will return None
                    features.append('containNum')
                if re.search(r'-', curW):
                    features.append('containHyp')
                #generate affix features for the current word
                #maximum length for prefix and suffix is 4, unless words are shorter
                if len(curW) >= 4:
                    end = 5
                else:
                    end = len(curW)
                for index in range(1, end):
                    pref = 'pref={}'.format(curW[:index])
                    suf = 'suf={}'.format(curW[-index:])
                    features.extend([pref, suf])
            else:
                #add curW to features
                features.append('curW={}'.format(curW))
            #add everything to a the word_label dict and to the feature_vecs counter
            for feature in features:
                feature_vecs[feature] += 1
                key = (sentence_index+1, word_tag_i-2, curW, curT) #start counting sentences from 1, start counting words from first real word (skip BOS's)
                word_label_features[key].add(feature)
    return feature_vecs, word_label_features

def get_feature_vector_output(input_sentences, feature_vectors, word_label_feat_dict):
    '''
    takes a nested list of sentences of word, tag tuples, progresses through the list and grabs the relevant
    feature vector information for each word based on the pre-made word_label_feat_dict
    :param train_inputlines: nested list of sentences of (word, tag) tuples
    :param feature_vectors: a Counter of feature_vector: count of how many times it appeared in training. Determines
    which of all vectors we will keep in the final file
    :param word_label_feat_dict: a pre-made dict of (sent_num, word_num, word, tag) : feature vectors
    :return: formatted string output to write a file
    '''
    output_lines = []
    #for replacing commas with "comma" because mallet is dumb and , is a delimiter
    comma = re.compile(r',')
    for sentence_index in range(len(input_sentences)):
        sentence = input_sentences[sentence_index]
        for word_tag_i in range(2, len(sentence)-2):
            curW, curT = sentence[word_tag_i]
            key = (sentence_index + 1, word_tag_i - 2, curW, curT)
            features = word_label_feat_dict[key]
            #restrict to only features in given Counter
            kept_features = comma.sub('comma', ' 1 '.join(set(features) & set(feature_vectors)))
            output_line = comma.sub('comma','{}-{}-{} {} {} 1'.format(key[0], key[1], key[2], key[3], kept_features))
            output_lines.append(output_line)
    output_data = '\n'.join(output_lines)
    return output_data


if __name__ == "__main__":
    train_filename, test_filename = sys.argv[1], sys.argv[2]
    rare_thres, feat_thres = int(sys.argv[3]), int(sys.argv[4])
    output_dir = sys.argv[5]

    #check if output_dir exists, if not, create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ####Part 1
    #process training file
    regex_obj = re.compile(r'(?<!\\)/')
    # list of tuples of (word, tag), one list per sentence
    train_inputlines = []
    with open(train_filename, 'rU') as infile:
        for line in infile:
            train_inputlines.append(process_sentence(line, regex_obj))
    # extract words from input lines
    words = [item[0] for sentence in train_inputlines for item in sentence]

    #generate vocabulary from words
    vocabulary = make_voc(words)
    #write a file with vocab
    voc_output = '\n'.join(['{} {}'.format(key, val) for key, val in vocabulary.most_common()])
    with open(output_dir + '/train_voc', 'w') as outfile:
        outfile.write(voc_output)

    ####Part 2
    #generate feature vectors
    feature_vectors, word_label_feat_dict = generate_feature_vectors(train_inputlines, vocabulary, rare_thres)
    init_feat_output = '\n'.join(['{} {}'.format(key, val) for key, val in feature_vectors.most_common()])
    with open(output_dir + '/init_feats', 'w') as outfile:
        outfile.write(init_feat_output)

    ####Part 3
    #remove features below feature threshold
    #would be nice to sort in ascending order so could stop traversing dictionary once reaches the threshold
    for feat, count in reversed(feature_vectors.most_common()):
        #check if the feature is curW, if so, keep it regardless
        label = feat.split('=')[0]
        if label == 'curW':
            continue
        else:
            if count < feat_thres:
                del feature_vectors[feat]
    #write a file with features that survived the pruning stage
    kept_feat_output = '\n'.join(['{} {}'.format(key, val) for key, val in feature_vectors.most_common()])
    with open(output_dir + '/kept_feats', 'w') as outfile:
        outfile.write(kept_feat_output)

    ####Part 4
    #generate train file based on pruned features
    train_output = get_feature_vector_output(train_inputlines, feature_vectors, word_label_feat_dict)
    with open(output_dir + '/final_train.vectors.txt', 'w') as outfile:
        outfile.write(train_output)

    ####Part 5
    #generate test_file based on pruned features
    #This is a repeat of step 4 but with the test file
    test_inputlines = []
    with open(test_filename, 'rU') as infile:
            for line in infile:
                test_inputlines.append(process_sentence(line, regex_obj))

    test_feature_vectors, test_word_label_feat_dict = generate_feature_vectors(test_inputlines, vocabulary, rare_thres)
    #don't actually need to use test_feature_vectors since we will be using feature_vectors from training.
    test_output = get_feature_vector_output(test_inputlines, feature_vectors, test_word_label_feat_dict)

    with open(output_dir + '/final_test.vectors.txt', 'w') as outfile:
            outfile.write(test_output)
