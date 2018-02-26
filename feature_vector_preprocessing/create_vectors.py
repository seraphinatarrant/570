'''
A script that creates training and test vectors from several directories of documents based on a given percentage split.
Command to run: create_vectors.py train_vector_file test_vector_file ratio dir1 dir2...etc

takes the percent given of the articles in the given directories and creates training data vectors with proc_file.py
also creates the train ones
'''

import sys
import os
import proc_file
import subprocess
import re

def get_dir_basename(path):
    '''
    :param path: a path like /dir_top/dir_mid/grab_this
    :return: the base (grab_this)
    '''
    return path.split('/')[-1]

def test_train_split(files, ratio):
    num_files = int(len(filenames))
    train_num = round(num_files * ratio)
    if train_num == num_files:
        train_num -= 1
        print("{} of {}, rounded, is {}. Might I suggest a larger corpus? Removing 1 file as test set".format(
            ratio, num_files, num_files), file=sys.stderr)
    if train_num == 0:
        train_num = 1
        print("{} of {}, rounded, is 0. Might I suggest a larger corpus? Keeping 1 file as training set".format(
            ratio, num_files), file=sys.stderr)
    train_files, test_files = files[:train_num], files[train_num:]
    return train_files, test_files

def format_output(input_filename, target_label, fv_counter):
    '''
    :param input_filename the name of the input file (for formatting)
    :param target_label the class_label (for formatting)
    :param fv_counter: A counter of word:freq
    :return: the list of output data
    '''
    feature_vlist = ' '.join(["{} {}".format(key, val) for key, val in sorted(fv_counter.items())])
    output_data = "{} {} {}".format(input_filename, target_label, feature_vlist)
    return output_data




if __name__ == "__main__":
    train_output_filename, test_output_filename = sys.argv[1], sys.argv[2]
    ratio = float(sys.argv[3])
    #grabs all given directories
    directories = sys.argv[4:]
    non_alpha = re.compile('[^A-Za-z]+')
    train_output_list, test_output_list = [], []
    for path in directories:
    #The first % ratio in each directory is training files, the rest is test files
        class_label = get_dir_basename(path)
        filenames = sorted(os.listdir(path))
        train_filenames, test_filenames = test_train_split(filenames, ratio)

        #for all files in train set, process data and then format output
        # for all files in test set, do same
        for file in train_filenames:
            full_filepath = '{}/{}'.format(path, file)
            feature_vector_data = proc_file.process_file(full_filepath)
            train_output_list.append(format_output(file, class_label, feature_vector_data))

        for file in test_filenames:
            full_filepath = '{}/{}'.format(path, file)
            feature_vector_data = proc_file.process_file(full_filepath)
            test_output_list.append(format_output(file, class_label, feature_vector_data))

    #write outputs
    with open(train_output_filename, 'w') as tr_outfile:
        tr_outfile.write('\n'.join(train_output_list))
    with open(test_output_filename, 'w') as te_outfile:
        te_outfile.write('\n'.join(test_output_list))


    