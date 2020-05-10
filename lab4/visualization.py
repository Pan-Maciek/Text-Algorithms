from distance import distance, mk_transition_matrix, transition, Insert, Skip, Delete, Substitute
import sys

default = '\u001b[0m'
red, green, yellow = (f'\u001b[{n}m' for n in [31, 32, 33])
store, restore = '\u001b[s', '\u001b[u'
clean_down = '\u001b[J'
show, hide = '\u001b[?25h', '\u001b[?25l'

data = [
    ('los', 'kloc'),
    ('Łódź', 'Lodz'),
    ('kwintesencja', 'quintessence'),
    ('ATGAATCTTACCGCCTCG', 'ATGAGGCTCTGGCCCTG')
]

print(hide)
for a, b in data:
    tmp = a

    sys.stdout.write(f'{store}')
    matrix = mk_transition_matrix(a, b)
    dist = distance(a, b, matrix=matrix)
    for action in transition(a, b, matrix=matrix):
        sys.stdout.write(f'{restore}{store}{clean_down}')
        if isinstance(action, Skip):
            print(f"{a}\n\u001b[{action.at+1}G^")
        elif isinstance(action, Insert):
            print(f"{a[:action.at]} {a[action.at:]}\n\u001b[{action.at+1}G^ {green}insert{default} {action.new}")
        elif isinstance(action, Delete):
            print(f"{a}\n\u001b[{action.at+1}G^ {red}delete{default} {action.old}")
        elif isinstance(action, Substitute):
            print(f"{a}\n\u001b[{action.at+1}G^ {yellow}substitute{default} {action.old} with {action.new}")
        a = action.apply(a)
        input()
    print(f'{restore}{clean_down}{tmp} -> {b} distance: {dist}\n')
sys.stdout.write(show)