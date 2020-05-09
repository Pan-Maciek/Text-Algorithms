import numpy as np
from dataclasses import dataclass

def delta(a, b):
    return 0 if a == b else 1

def distance(a, b, dt=delta):
    a_len, b_len = len(a), len(b)
    if a_len > b_len:
        a, b = b, a
        a_len, b_len = b_len, a_len
    
    row1 = np.fromiter(range(a_len + 1), count=a_len + 1, dtype=float)
    row2 = np.empty(a_len + 1, dtype=float)

    for x in range(b_len):
        row2[0] = x + 1
        for y in range(a_len):
            row2[y+1] = min(
                row1[y] + dt(a[y], b[x]), 
                row1[y+1] + 1, 
                row2[y] + 1
            )
        row1, row2 = row2, row1
    return row1[-1]

@dataclass
class Insert:
    at: int
    new: chr

    def apply(self, str):
        return str[:self.at] + self.new + str[self.at:]
    
    def undo(self, str):
        return str[:self.at] + str[self.at+1:]

@dataclass
class Delete:
    at: int
    old: chr

    def apply(self, str):
        return str[:self.at] + str[self.at+1:]

    def undo(self, str):
        return str[:self.at] + self.old + str[self.at:]

@dataclass
class Substitute:
    at: int
    new: chr
    old: chr

    def apply(self, str):
        return str[:self.at] + self.new + str[self.at+1:]

    def undo(self, str):
        return str[:self.at] + self.old + str[self.at+1:]

def mk_transition_matrix(a, b, dt=delta):
    x, y = len(a) + 1, len(b) + 1

    m = np.empty((x, y), dtype=float)
    m[:, 0], m[0, :] = range(x), range(y) # initialize edges

    for x, y in np.ndindex((x-1, y-1)):
        m[x+1, y+1] = min(
            m[x, y] + dt(a[x], b[y]), # update
            m[x+1, y] + 1, # insert
            m[x, y+1] + 1  # delete
        )

    return m

def transition(a, b, dt=delta):
    m = mk_transition_matrix(a, b, dt)
    x, y = len(a), len(b)

    while (x, y) != (0, 0):
        x, y, transition = min(
            (x-1, y-1, None if a[x-1] == b[y-1] else Substitute(x-1, b[y-1], a[x-1])),
            (x-1, y, Delete(x-1, a[x-1])),
            (x, y-1, Insert(x, b[y-1])),
            key=lambda x: m[x[0], x[1]]
        )
        if transition:
            yield transition
