import numpy as np
from dataclasses import dataclass

def delta(a, b):
    return 0 if a == b else 1

def mk_transition_matrix(a, b, dt=delta):
    x, y = len(a) + 1, len(b) + 1

    m = np.empty((x, y), dtype=int)
    m[:, 0], m[0, :] = range(x), range(y) # initialize edges

    for x, y in np.ndindex((x-1, y-1)):
        m[x+1, y+1] = min(
            m[x, y] + dt(a[x], b[y]), # update
            m[x+1, y] + 1, # insert
            m[x, y+1] + 1  # delete
        )

    return m

def distance(a, b, dt=delta, m=None):
    m = m or mk_transition_matrix(a, b, dt)
    return m[len(a), len(b)]

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


def transition(a, b, dt=delta, m=None):
    m = m or mk_transition_matrix(a, b, dt)
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
