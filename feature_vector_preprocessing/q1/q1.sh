#!/bin/sh

#set -x
PATH=/NLP_TOOLS/tool_sets/mallet/latest/bin:$PATH
CLASSPATH=/NLP_TOOLS/tool_sets/mallet/latest/lib/mallet-deps.jar:$CLASSPATH
#export z=purple
#echo Hi from foo, z=$
#set +x
#export zz=ls

#eval $zz
trainers="NaiveBayes MaxEnt DecisionTree Winnow BalancedWinnow"


#example with different trainers
for trainer in $trainers
do
    eval vectors2classify --training-file /dropbox/17-18/570/hw8/examples/train.vectors --testing-file /dropbox/17-18/570/hw8/examples/test.vectors --trainer $trainer > $trainer.stdout 2>$trainer.stderr
done
