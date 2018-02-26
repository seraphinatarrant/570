#!/bin/sh

set -x
PATH=/NLP_TOOLS/tool_sets/mallet/latest/bin:$PATH
CLASSPATH=/NLP_TOOLS/tool_sets/mallet/latest/lib/mallet-deps.jar:$CLASSPATH
export z=purple
echo Hi from foo, z=$
set +x