'''
A scratch that plays around with various maths that are important for neural nets
'''

import numpy as np

def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()



if __name__ == "__main__":
    scores = [1.0, 2.0, 3.0]
    print(softmax(scores))
    sum = np.sum(np.exp(range(1, 4)))
    print(sum)
    softmax_scores = [(np.exp(score))/sum for score in scores]
    print(softmax_scores)
