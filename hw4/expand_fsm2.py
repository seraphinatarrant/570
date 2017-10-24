'''
this pair is similar to the expand1 and acceptor 1, but instead of outputting whether the string is accepted,
it outputs which part of the word belongs to which rule (if accepted) and *NONE* otherwise
output format:
speaks => speak/irreg_verb_stem s/3sg
speaking => speak/irreg_verb_stem ing/pres_part
spoke => spoke/irreg_past_verb_form
speak => speak/irreg_verb_stem
speaked => *NONE*


So instead of making it an fsm, we make it an fst that outputs all of the parts and also the class of the word
'''

import sys
from collections import defaultdict

import re


def expand_fsm(morph_fsm,lexicon):
    '''
    :param morph_fsm: an fsm of morph rules, initial state, final state, transitions dict
    :param lexicon: a lexicon list made with import_lexicon function
    :return: an expanded fst with input output pairs. Currently does not do any minimisation
    '''
    start_state, final_state, existing_states = morph_fsm[1], morph_fsm[0], set()
    empty_symbol = '*e*'
    # existing states to track states that are already being used to prevent naming collisions
    print(final_state)
    for entry in lexicon:
        word, class_label = entry[0], entry[1]
        try:
            transitions = morph_fsm[2][class_label].items() #will return a list of tuples of (from state,list of to states)
            for transition in transitions: #loop through the list of returned transitions
                from_state, to_states = transition[0], transition[1] #remember that to_state might be a list
                existing_states.add(from_state)
                [existing_states.add(next) for next in to_states]
                for char in word:       #loop through word expanding the fsm for each character. This time go through to the final char
                    next_state = from_state+char #next state name is the from state + the next character
                    if next_state in existing_states: #check uniqueness to prevent collisions of state names
                        unique_state = False
                        count = 0
                        while not unique_state:
                            next_state = next_state+str(count) #could do randint instead....if I wanted to but then it wouldn't be the same each time
                            if next_state not in existing_states:
                                unique_state = True
                            count+=1
                    print('({} ({} {} {}))'.format(from_state, next_state, char, char))
                    existing_states.add(next_state)
                    from_state = next_state
                #print final transition from last state to the to_state, with an epsilon and the word label
                for to_state in to_states:
                    print('({} ({} {} {}))'.format(from_state, to_state, empty_symbol, '/{}'.format(class_label))) #input is nothing, output is class_label
        except KeyError:
            print('{} was not in morphotactic fsm rules'.format(class_label), file=sys.stderr)
        #need to also account for epsilon transitions
    try:
        epsilon_transitions = morph_fsm[2]['*e*'].items()
        for transition in epsilon_transitions:  #yes this is copy pasted so it should be a function... but oh well for now
            e_from_state, e_to_states = transition[0], transition[1] #remember could be list
            for e_to_state in e_to_states:
                print('({} ({} {} {}))'.format(e_from_state, e_to_state, empty_symbol, empty_symbol))

    except KeyError:
        pass


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
    expand_fsm(morph_rules, lexicon)