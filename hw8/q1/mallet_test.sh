#!/bin/sh

#set -x
PATH=/NLP_TOOLS/tool_sets/mallet/latest/bin:$PATH
CLASSPATH=/NLP_TOOLS/tool_sets/mallet/latest/lib/mallet-deps.jar:$CLASSPATH
#export z=purple
#echo Hi from foo, z=$
#set +x


#creates a data vector
eval mallet import-dir --input /dropbox/17-18/570/hw8/20_newsgroups/talk.politics.* --skip-header --output politics.vectors

#converts politics.vectors into text format
eval vectors2info --input politics.vectors --print-matrix siw > politics.vectors.txt

#converts politics.vectors into training and test files
eval vectors2vectors --input politics.vectors --training-portion 0.9 --training-file train1.vectors --testing-file test1.vectors

#trains and tests. accuracy info at end of stdout
eval vectors2classify --training-file train1.vectors --testing-file test1.vectors --trainer DecisionTree > dt.stdout 2>dt.stderr
