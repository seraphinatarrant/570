'''
A script that takes 3 args and implements a word analogizer for word embeddings
Command to run: word_analogy.py vector_file input_dir output_dir normalise similarity

normalise: if non-zero, normalise word embedding vecotrs first. Else use original vectors.
similarity: if non-zero, use cosine. else use Euclidean

A:B is like C:D
Represent each word as a word vector x_w

Compute x_d (target word) = x_b - x_a + x_c (because in an analogy x_b - x_a = x_d - x_c)
Find w* = argmax_w sim(x_w, x_d) #find the word that is most similar to x_d


store vectors as an word2idx map and an array of vectors
if a word is OOV, treat it as a zero-vector



Cosine:
athens greece baghdad *iraq*
athens greece bangkok bangkok
athens greece beijing beijing
athens greece berlin germany
athens greece bern bern
athens greece cairo *greece*
athens greece canberra *belgium*
athens greece hanoi hanoi
athens greece havana *cuba*
athens greece helsinki *finland*
athens greece islamabad islamabad
athens greece kabul afghanistan

Euclidean:
athens greece baghdad baghdad
athens greece bangkok bangkok
athens greece beijing beijing
athens greece berlin germany
athens greece bern bern
athens greece cairo *greece*
athens greece canberra canberra
athens greece hanoi hanoi
athens greece havana havana
athens greece helsinki *finland*
athens greece islamabad islamabad
athens greece kabul afghanistan

Lesson:
For me, the bottleneck was getting the similarity metrics for the "d vector", comparing it with every blessed entry in
what was read in from `vectors.txt`.  It was excruciatingly slow in a for loop, but it's much faster if you do
everything all in one go using `numpy`.  By "everything in one go", I mean return a single `numpy array` of 71280
cosine distances (say) without using a for loop, but using `numpy`'s broadcasting rules to crunch on entire vectors,
instead of one value at at time.

Like Example 5
http://scipy.github.io/old-wiki/pages/EricsBroadcastingDoc
'''

import sys
import os
import numpy as np
from collections import defaultdict


def read_vectors(input_file, norm_flag):
    '''
    Reads in a word vector input file and creates a dict of word to index mappings, and a list of arrays of vectors.
    If norm > 0, then the vectors will be normalised.

    :param input_file: a word vector file of format word v1 v2 v3, one word vector per line
    :param norm_flag: an int to determine whether to normalise vectors
    :return: default dict of word to index mapping, array of vectors
    '''
    word2index = {}
    index2word = defaultdict(str)
    current_index = 0
    vec_array = []
    first = True
    with open(input_file, 'rU') as infile:
        for line in infile:
            tokens = line.strip().split()
            #in our example all the vector sizes are 50, but I am not sure that is given so allow to be anything.
            word, vector = tokens[0], np.array(list(map(float, tokens[1:]))) #use something other than slice here so it is faster
            #put word in dict. Note that it DOES NOT check for uniqueness, if there was an error in the input file only
            # the most recent version of the word will be kept
            if first:
                vec_length = vector.size  # since it is 1D vector
                first = False
            else:
                if vector.size != vec_length:
                    sys.exit('Vectors are not all of same shape. There is an error in '
                             '{} for word {}'.format(input_file, word))
            word2index[word] = current_index
            index2word[current_index] = word
            current_index += 1
            if norm_flag:
                #make normalised vector
                norm_constant = np.square(vector).sum()**.5
                norm_vector = np.divide(vector, norm_constant)
                vec_array.append(norm_vector)
            else:
                vec_array.append(vector)
    vec_array_np = np.array(vec_array) #make a vector of vectors

    return word2index, index2word, vec_array_np, vec_length


def cosine_sim(x_d, vec_array):
    #best_w, best_vec, best_d = None, None, -2 #set to values that will be overwritten as all cosine sim > -2
    #for word in word2index:
    #    vec = vec_array[word2index[word]]
    #    co_sim = 1 - spatial.distance.cosine(x_d, vec)
    #    if co_sim > best_d:
    #        best_w, best_vec, best_d = word, vec, co_sim

    #return best_w
    #take dot product of 2 vectors. which reduces dimensionality and gives me an array of results.
    #IMPORTANT that vec_array is first arg as a result
    dot_prod_array = np.dot(vec_array, x_d)
    len_vec_array, len_x_d = (vec_array**2).sum(axis=1)**.5, (x_d**2).sum()**.5
    cosine_sim_array = np.divide(dot_prod_array, len_vec_array*len_x_d)
    best_vec_index = np.argmax(cosine_sim_array)

    return best_vec_index


def euclidean_dist(x_d, vec_array):
    '''
    Compares given vector with array of vectors and finds one with closest Euclidean distance.
    :param x_d:
    :param vec_array: array of vectors
    :return: the index of the winning vector
    '''
    #Sqrt of (sum of (x_i - y_i)^2 for all n of vector)
    results = (((x_d - vec_array)**2).sum(axis=1))**.5 #axis = 0 sums over columns, axis = 1 sums over rows
    best_vec_index = np.argmin(results)
    return best_vec_index


def compute_analogies(word2index, index2word, vec_array, vec_length, input_dir, output_dir, sim):
    '''
    Computes a new target D for each given analogy A B C D. And compares the new D to the given D and prints out an
    accuracy to stdout.
    :param word2index: a dict of word to index mappings to retrieve vectors from the vector array for a given word
    :param index2word: the reverse, to retrieve the word after find the index of the best vector
    :param vec_array: a numpy array of vectors
    :paran vec_length: the length of the vectors
    :param input_dir: directory of the input files
    :param output_dir: directory to write output files to (with the same name)
    :param sim: a flag that if 0 uses Euclidean similarity, if >0 uses cosine
    :return: none - writes all files to output dir and accuracy info to stdout
    '''
    zero_vec = np.zeros(vec_length)
    files = sorted(os.listdir(input_dir))
    #files = ['capital-common-countries.txt']
    for filename in files:
        output_lines = []
        with open(os.path.join(input_dir, filename), 'rU') as infile:
            total = 0
            total_corr = 0
            for line in infile:  # for every line find new D
                if line:  # grab A, B, C words and convert to indexes with dict
                    w_a, w_b, w_c, w_d = line.strip().split()
                    a_b_c_vec = []
                    for word in w_a, w_b, w_c:
                        index = word2index.get(word, -1)  # this handles OOV words
                        if index >= 0:
                            next_vec = vec_array[index]
                        else:
                            next_vec = zero_vec
                        a_b_c_vec.append(next_vec)
                    x_a, x_b, x_c = a_b_c_vec
                    # calc the target vector
                    x_d = x_b - x_a + x_c
                    # find word closest to x_d vector
                    if sim:  # use cosine similarity
                        win_index = cosine_sim(x_d, vec_array)
                    else:
                        # use Euclidean distance
                        win_index = euclidean_dist(x_d, vec_array)
                    winner = index2word[win_index]
                    #update totals
                    total += 1
                    if winner == w_d:
                        total_corr += 1
                    output_line = '{} {} {} {}'.format(w_a, w_b, w_c, winner)
                    output_lines.append(output_line)
        #print accuracy
        print('{}:'.format(filename))
        print('ACCURACY TOP1: {}% ({}/{})'.format(total_corr/total*100, total_corr, total))
        #write to output dir
        with open(os.path.join(output_dir, filename), 'w') as outfile:
            outfile.write('\n'.join(output_lines))


if __name__ == "__main__":
    vector_file, input_dir, output_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    norm, sim = int(sys.argv[4]), int(sys.argv[5])
    #print('Normalise y/n: {}, Sim: {}. >0 is cosine similarity, 0 is Euclidean'.format(norm, sim))

    #check if output_dir exists, if not, create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    word2index, index2word, vec_array, vec_length = read_vectors(vector_file, norm)
    compute_analogies(word2index, index2word, vec_array, vec_length, input_dir, output_dir, sim)

