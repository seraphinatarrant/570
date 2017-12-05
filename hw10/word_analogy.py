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


Euclidean formula
'''

import sys, os
import math
import numpy as np
from scipy import spatial
from collections import defaultdict

def read_vectors(input_file, norm_flag):
    '''
    Reads in a word vector input file and creates a dict of word to index mappings, and a list of arrays of vectors.
    If norm > 0, then the vectors will be normalised.

    :param input_file: a word vector file of format word v1 v2 v3, one word vector per line
    :param norm_flag: an int to determine whether to normalise vectors
    :return: default dict of word to index mapping, array of vectors
    '''
    word2index = defaultdict(int)
    current_index = 0
    vec_array = []
    with open(input_file, 'rU') as infile:
        for line in infile:
            tokens = line.strip().split()
            #in our example all the vector sizes are 50, but I am not sure that is given so allow to be anything.
            word, vector = tokens[0], np.array(list(map(float, tokens[1:]))) #use something other than slice here so it is faster
            #put word in dict. Note that it DOES NOT check for uniqueness, if there was an error in the input file only
            # the most recent version of the word will be kept
            word2index[word] = current_index
            current_index += 1
            if norm_flag:
                #make normalised vector
                norm_constant = math.sqrt(np.square(vector).sum())
                norm_vector = np.divide(vector, norm_constant)
                vec_array.append(norm_vector)
            else:
                vec_array.append(vector)

    return word2index, vec_array




def cosine_sim(x_d, word2index, vec_array):
    best_w, best_vec, best_d = None, None, -2 #set to values that will be overwritten as all cosine sim > -2
    for word in word2index:
        vec = vec_array[word2index[word]]
        co_sim = 1 - spatial.distance.cosine(x_d, vec)
        if co_sim > best_d:
            best_w, best_vec, best_d = word, vec, co_sim

    return best_w


def euclidean_dist(x_d, vec_array):
    #for each vector in vec, calc Euclidean distance
    #Sqrt of (sum of (x_i - y_i)^2 for all n of vector)
    #keep track of closest
    best, best_d = #first_vector, dist x_d and first vector
    for vec in vec_array:
        #calc distance
        if dist < best:
            best, best_d = vec, dist
    return best

if __name__ == "__main__":
    vector_file, input_dir, output_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    norm, sim = sys.argv[4], sys.argv[5]
    #check if output_dir exists, if not, create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    word2index, vec_array = read_vectors(vector_file, norm)
    #go through each file in directory (currently does nothing with subdir if there)
    #for root, dirs, files in os.walk(input_dir):

    #files = sorted(os.listdir(input_dir))
    files = ['capital-world.txt']
    for filename in files:
        with open(os.path.join(input_dir, filename), 'rU') as infile:
            for line in infile: #for every line find new D
                if line: #grab A, B, C words and convert to indexes with dict
                    w_a, w_b, w_c, w_d = line.strip().split()
                    x_a, x_b, x_c = vec_array[word2index[w_a]], vec_array[word2index[w_b]], \
                                        vec_array[word2index[w_c]]
                    #calc the target vector
                    x_d = x_b - x_a + x_c
                    #find word closest to x_d vector
                    if sim:
                        # use cosine similarity
                        cosine_sim(x_d, vec_array) #make sure this is vec if not normalised or norm_vec if normalised.
                    else:
                    #use Euclidean distance
                        euclidean_dist(x_d, vec_array)


