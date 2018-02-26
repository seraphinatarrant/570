#!/bin/sh

python3 maxent_tagger.py $@

PATH=/NLP_TOOLS/tool_sets/mallet/latest/bin:$PATH
CLASSPATH=/NLP_TOOLS/tool_sets/mallet/latest/lib/mallet-deps.jar:$CLASSPATH

eval mallet import-file --input $5/final_train.vectors.txt --output $5/final_train.vectors
eval mallet import-file --input $5/final_test.vectors.txt --output $5/final_test.vectors --use-pipe-from $5/final_train.vectors
eval mallet train-classifier --training-file $5/final_train.vectors --testing-file $5/final_test.vectors --trainer MaxEnt --output-classifier $5/me_model --report train:accuracy --report test:accuracy > $5/me_model.stdout 2> $5/me_model.stderr
eval mallet classify-file --input $5/final_test.vectors.txt --classifier $5/me_model --output sys_out