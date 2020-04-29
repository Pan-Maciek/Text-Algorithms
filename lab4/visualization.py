from distance import * 
import sys

default = '\u001b[0m'
red, green, yellow = (f'\u001b[{n}m' for n in [31, 32, 33])
store, restore = '\u001b[s', '\u001b[u'
clean_down = '\u001b[J'

data = [
    ('los', 'kloc'),
    ('Łódź', 'Lodz'),
    ('kwintesencja', 'quintessence'),
    ('ATGAATCTTACCGCCTCG', 'ATGAGGCTCTGGCCCTG')
]

print()
for a, b in data:
    tmp = a

    sys.stdout.write(f'{store}')
    dist = distance(a, b)
    for action in list(transition(a, b)):
        sys.stdout.write(f'{restore}{clean_down}')
        if isinstance(action, Insert):
            print(f"{a[:action.at]} {a[action.at:]}\n\u001b[{action.at+1}G^ {green}insert{default} {action.new}")
        elif isinstance(action, Delete):
            print(f"{a}\n\u001b[{action.at+1}G^ {red}delete{default} {action.old}")
        elif isinstance(action, Substitute):
            print(f"{a}\n\u001b[{action.at+1}G^ {yellow}substitute{default} {action.old} with {action.new}")
        a = action.apply(a)
        input()
    print(f'{restore}{clean_down}{tmp} -> {b} distance: {dist}\n')