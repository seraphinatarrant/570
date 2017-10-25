#command line expandfsm1.py lexicon morph_rules output fssm
#builds an expanded FSM given a lexicon and morphotactic rules.

'''
So the lexicon will be in format:
word classLabel

take input of morph rules (carmel format FSA) and input of lexicon
and build an FSM file for the lexicon that transitions on state character by character.

E.g. Given the rule: `(q0 (q2 irreg_verb_stem))` and lexicon entry `sing irreg_verb_stem`,
proper expansion is something like this

(q0 (q0s s))
(q0s (q0si i))
(q0si (q0sin n))
(q0sin (q2 g))

To Do:
***important to be careful about naming the states since there will be loads.
Make sure if there is ambiguity we just enumerate all possibilities
'''

import sys
from collections import defaultdict

import re


def expand_fsm(morph_fsm,lexicon):
    '''
    :param morph_fsm: an fsm of morph rules, initial state, final state, transitions dict
    :param lexicon: a lexicon list made with import_lexicon function
    :return: an expanded fsm. Currently does not do any minimisation
    '''
    start_state, final_state, existing_states = morph_fsm[1],morph_fsm[0],set()
    # existing states to track states that are already being used to prevent naming collisions
    output_list = []
    output_list.append(final_state)
    output_list.append('({} ({} *e*))'.format(start_state,start_state)) #this ensures that the start state comes first
    for entry in lexicon:
        word, class_label = entry[0], entry[1]
        try:
            transitions = morph_fsm[2][class_label].items() #will return a list of tuples of (from state,list of to states)
            for transition in transitions: #loop through the list of returned transitions
                from_state, to_states = transition[0], transition[1] #remember that to_state might be a list
                existing_states.add(from_state)
                [existing_states.add(next) for next in to_states]
                for char in word[:-1]:       #loop through word expanding the fsm for each character
                    next_state = from_state+char #next state name is the from state + the next character
                    if next_state in existing_states: #check uniqueness to prevent collisions of state names
                        unique_state = False
                        count = 0
                        while not unique_state:
                            next_state = next_state+str(count)
                            if next_state not in existing_states:
                                unique_state = True
                            count+=1
                    output_list.append('({} ({} {}))'.format(from_state, next_state, char))
                    existing_states.add(next_state)
                    from_state = next_state
                #print final transition from last char to the to_state
                for to_state in to_states:
                    output_list.append('({} ({} {}))'.format(from_state, to_state, word[-1:]))
        except KeyError:
            print('{} was not in morphotactic fsm rules'.format(class_label), file=sys.stderr)
        #need to also account for epsilon transitions
    try:
        epsilon_transitions = morph_fsm[2]['*e*'].items()
        for transition in epsilon_transitions:  #yes this is copy pasted so it should be a function... but oh well for now
            e_from_state, e_to_states = transition[0], transition[1] #remember could be list
            for e_to_state in e_to_states:
                output_list.append('({} ({} {}))'.format(e_from_state, e_to_state, '*e*'))

    except KeyError:
        pass
    return output_list


def import_morphotactics(file):
    '''
    builds a dict of morphotactic rules. A little different than in the past, since we want to look up by class label
    so the organisation is {classlabel: {from_state: [to_state1, to_state2]} so a dict of dict of list.
    This is veryyyyy similar to hw1 fsa acceptor, but just accesses by label rather than by current state first.
    :param file: a file of morphotactic rules in carmel format. E.g. (q0 (q3 irreg_past_verb_form)). One rule per line.
    :return: dict of morphotactic rules in this format
    '''
    line_list = []
    with open(file, 'rU') as file:
        line_list = [line.strip() for line in skip_pycomments(file)]

    final_states = line_list[0]  # only accepts one final state
    initial_state = replace_parens(line_list[1])[0]  # grabs first element of the list returned as carmel files
    # specify start state as first state in second line of file
    # time to build the transitions dict
    transitions = defaultdict(defaultdict)
    for line in line_list[1:]:
        if line:
            new_trans = replace_parens(line)
            state, label, next_state = new_trans[0], new_trans[2], new_trans[1]
            if not transitions[label]: #if label not in dict then assign a new dict of lists
                transitions[label] = {state:[next_state]} #make sure these dictionary assignments work
            else:
                try:
                    if transitions[label][state]: #check next layer of nesting
                        transitions[label][state].append(next_state)
                except KeyError:
                    transitions[label][state] = [next_state]

    return [final_states, initial_state, transitions]

def import_lexicon(file):
    '''
    reads in lexicon and returns dict of words and classlabels.
    Explicitly no processing it done at the character level - all input is assumed valid if it conforms to format
    :param file: the name/path to a file one word and classlabel per line whitespace separated
    :return: dict of word:classlabel
    '''
    with open(file, 'rU') as file:
        lexicon_list = []
        count = 1 #for error use
        for line in file:
            new_line = line.strip().split()
            if new_line:
                if len(new_line) == 2:
                    entry = (new_line[0], new_line[1])
                    lexicon_list.append(entry)
                else:
                    print('Lexicon input format incorrect on line {}, which is being skipped: {}'.format(count, line), file=sys.stderr)
            count += 1
    return lexicon_list

def skip_pycomments(input):
    for line in input:
        line = line.strip()
        if line:
            if not line.lstrip().startswith('#'):
                yield line

def replace_parens(line):
    return re.sub('(\)|\()',' ',line).split()


if __name__ == "__main__":
    lexicon = import_lexicon(sys.argv[1])
    morph_rules = import_morphotactics(sys.argv[2])
    output_file_name = sys.argv[3]
    with open(output_file_name, 'w') as file:
        file.write('\n'.join(expand_fsm(morph_rules, lexicon)))
   #print(lexicon)
   #print(morph_rules[2])