#!/bin/sh

#set -x
PATH=/NLP_TOOLS/tool_sets/mallet/latest/bin:$PATH
CLASSPATH=/NLP_TOOLS/tool_sets/mallet/latest/lib/mallet-deps.jar:$CLASSPATH
#export z=purple
#echo Hi from foo, z=$
#set +x


#creates a data vector
eval mallet import-file --input /dropbox/17-18/570/hw8/20_newsgroups/talk.politics.* --skip-header --output politics.vectors

#converts politics.vectors into text format
eval vectors2info --input politics.vectors --print-matrix siw > politics.vectors.txt

#converts politics.vectors into training and test files
eval vectors2vectors --input politics.vectors --training-portion 0.9 --training-file train1.vectors --testing-file test1.vectors

#trains and tests. accuracy info at end of stdout
eval vectors2classify --training-file train1.vectors --testing-file test1.vectors --trainer DecisionTree > dt.stdout 2>dt.stderr



    ####Run mallet commands. This part is totally separate and just uses mallet to get training and test accuracy and
    ####to generate and me-model
    #make train and test files into binary files
    subprocess.run('mallet import-file --input {} --output {}'.format(
        train_output_filename, output_dir + '/final_train.vectors'), shell=True)
    subprocess.run('mallet import-file --input {} --output {}'.format(
        test_output_filename, output_dir + '/final_test.vectors'), shell=True)

    subprocess.run('mallet train-classifier --training-file {0}/final_train.vectors --testing-file {0}/final_test.vectors '
                   '--trainer MaxEnt --output-classifier {0}/me_model '
                   '--report train:accuracy --report test:accuracy '
                   '> {0}/me_model.stdout 2> {0}/me_model.stderr'.format(output_dir), shell=True)