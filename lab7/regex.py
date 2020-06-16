from itertools import count
from string import whitespace, digits, ascii_letters

sigma = 1

class chr_set:
    def __init__(self, values, inv=False):
        self.inv = inv
        self.values = set(values)

    def __contains__(self, value):
        return (value not in self.values) if self.inv else (value in self.values)

class transition:
    def __init__(self, transition, target):
        self.target = target
        self.transition = transition

    def __contains__(self, key):
        return key in self.transition

class nfa_state:
    def __init__(self):
        self.transitions = []
        self.sigma_transitions = []
        self.accepting = False

    def __setitem__(self, key, value):
        if key == sigma:
            self.sigma_transitions.append(value)
        else:
            self.transitions.append(transition(key, value))

def build_nfa(expr):
    state, states = count(0), []
    it = iter(expr)

    def new_state():
        states.append(nfa_state())
        return next(state)

    def parse_set():
        r = set()
        c, prev = next(it), None
        inverted = c == '^'
        if c != '^':
            prev = c
            r.add(c)

        for c in it:
            if c == ']':
                break
            elif c == '-' and prev:
                c = next(it)
                if c == ']':
                    r.add('-')
                    break
                r |= {chr(c) for c in range(ord(prev) + 1, ord(c) + 1)}
                prev = None
            else:
                prev = c
                r.add(c)
        return chr_set(r, inv=inverted)

    def build(prev):
        stack = [prev]

        for c in it:
            if c == '(':
                stack.append(build(stack[-1]))
            elif c == ')':
                return stack[-1]
            elif c == '?':
                states[stack[-2]][sigma] = stack[-1]
            elif c == '+':
                states[stack[-1]][sigma] = stack[-2]
            elif c == '*':
                B = stack.pop()
                A = stack[-1]
                D, C = new_state(), new_state()
                stack.append(C)

                states[D].transitions = states[A].transitions
                states[D].sigma_transitions = states[A].sigma_transitions

                states[A].transitions = []
                states[A].sigma_transitions = []

                states[A][sigma] = states[B][sigma] = D
                states[A][sigma] = states[B][sigma] = C
            else:
                stack.append(new_state())
                if c == '\\':
                    n = next(it)
                    if   n == 'd': n = chr_set(digits)
                    elif n == 'D': n = chr_set(digits, inv=True)
                    elif n == 'w': n = chr_set(f'{ascii_letters}{digits}_')
                    elif n == 'W': n = chr_set(f'{ascii_letters}{digits}_', inv=True)
                    elif n == 's': n = chr_set(whitespace)
                    elif n == 'S': n = chr_set(whitespace, inv=True)
                    else:          n = chr_set(n)
                elif c == '[': n = parse_set()
                elif c == '.': n = chr_set([], inv=True)
                else:          n = chr_set(c)
                states[stack[-2]][n] = stack[-1]

        return stack[-1]

    build(new_state())
    states[-1].accepting = True
    return states

def test(regex, text):
    nfa = build_nfa(regex)
    length = len(text)

    def test(state, index, sigma):
        if index < length:
            c = text[index]
            for t in nfa[state].transitions:
                if c in t:
                    if test(t.target, index + 1, set()):
                        return True
        for t in nfa[state].sigma_transitions:
            if t not in sigma:
                sigma.add(t)
                if test(t, index, sigma):
                    return True

        return nfa[state].accepting and index == length

    return test(0, 0, set())

def find(regex, text):
    nfa = build_nfa(regex)
    length = len(text)

    def find(state, index, sigma):
        if index < length:
            c = text[index]
            for t in nfa[state].transitions:
                if c in t:
                    succ, i = find(t.target, index + 1, set())
                    if succ:
                        return True, i
        for t in nfa[state].sigma_transitions:
            if t not in sigma:
                sigma.add(t)
                succ, i = find(t, index, sigma)
                if succ:
                    return True, i

        return nfa[state].accepting, index

    index = 0
    while index < length:
        succ, i = find(0, index, set())

        if succ:
            yield text[index:i], index, i
            if i == index: # for regex with can match none for example a*
                i += 1
            index = i
        else:
            index += 1
