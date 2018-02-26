Q3
a) I stored the input FST in a triple nested dictionary of the form:
{'S3': {'can': {('S4', 'NOUN'): '0.4'}, 'fish': {('S4', 'NOUN'): '0.6'}},
'S0': {'they': {('S1', 'PRO'): '1.0'}},
'S2': {'can': {('S3', 'VERB'): '0.7'}, 'fish': {('S3', 'VERB'): '0.3'}},
'S1': {'can': {('S2', 'AUX'): '0.8', ('S3', 'VERB'): '0.1'}, 'fish': {('S3', 'VERB'): '0.1'}}}

The root of the dictionary tree is the initial state, the next level is the input, and the next level is a tuple key of
the next state + output with the probability as value.
I chose this structure to support quick lookups of information and to enforce key uniqueness while still ensuring
correct logic (ie there is never a legitimate case where there would be more than one tuple of (next state,output)
from a given state on a given input. If a document was constructed where that was the case the transitions could be
merged.

I also used a double nested dictionary to represent the state_table necessary to remember previous states and timesteps
for the recursive Viterbi backtrace. It has form {state: {index : predecessor info}} where predecessor info is
a tuple of (previous state, output from the transition, probability from start).

I initially approached the problem thinking I could augment dijkstra's with backtrace by having nodes remember their predecessor,
so I made a graph class. I later realised this could not handle cycles, and created the states and timesteps table (which is standard
Viterbi).
The graph object is still around for future anthropologists, and in case I decide I want it in future :). It is unnecessary though,
other than being nice for readability.

b) To make Viterbi work with FST, I had to not just track what transitions were available for a given input but to also
track the output from that transition - which I did with a state table (nested dict) as mentioned above .
The main difficulty here is that it is valid for a state with to have multiple transitions on the same given input with
different outputs, e.g. S1 -> S2 on "fish" with output "VERB" or "NOUN".

The code is commented as usual so it should be semi-readable if necessary. And there are sys errors on invalid inputs.

