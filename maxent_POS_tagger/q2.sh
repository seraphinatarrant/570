#!/bin/sh

thresholds="1_1 1_3 2_3 3_5 5_10"

for thres in $thresholds
do
    start='date +%s'
    rare=${thres:0:1}
    feat=${thres:2:1}
    echo running tagger with threshold $thres
    eval ./maxent_tagger.sh examples/wsj_sec0.word_pos examples/test.word_pos $rare $feat res_$thres
    end='date +%s'
    runtime=$((end-start))
    echo $runtime
done


#for trainer in $trainers
#do
#    eval vectors2classify --training-file /dropbox/17-18/570/feature_vector_preprocessing/examples/train.vectors --testing-file /dropbox/17-18/570/feature_vector_preprocessing/examples/test.vectors --trainer MaxEnt --output-classifier me-model > me_model.stdout 2>me_model.stderr
#done