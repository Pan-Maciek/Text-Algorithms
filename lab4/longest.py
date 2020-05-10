import numpy as np
from distance import distance, delta2

def longest(a, b):
    x, y = len(a) + 1, len(b) + 1

    m = np.zeros((x, y), dtype=int)
    for x, y in np.ndindex((x-1, y-1)):
        m[x+1, y+1] = (m[x, y] + 1) if a[x] == b[y] else max(m[x+1, y], m[x, y+1])
    
    out = []
    x, y = len(a), len(b)
    while x != 0 and y != 0:
        if m[x-1, y] == m[x, y]:
            x -= 1
        elif m[x, y-1] == m[x, y]:
            y -= 1
        else:
            x -= 1
            y -= 1
            out.append(a[x])
    out.reverse()
    return out

def lcs1(a, b):
    return (len(a) + len(b) - int(distance(a, b, delta2))) // 2