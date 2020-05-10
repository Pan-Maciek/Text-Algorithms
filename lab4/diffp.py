from longest import longest
from itertools import takewhile, chain

def diff_section(start, changes):
    length = len(changes)
    return f"{start+1},{start+length}" if length != 1 else f"{start+1}"

def diff(x, y):
    x_line, y_line = 0, 0
    x_len, y_len = len(x), len(y)
    edits = []
    for common in chain(longest(x, y), [None]):
        if x_line < x_len and x[x_line] != common:
            changes = [f'< {line}' for line in takewhile(lambda line: line != common, x[x_line:])]
            edits.append(f'{diff_section(x_line, changes)}d{y_line}\n')
            edits.extend(changes)
            x_line += len(changes)

        if y_line < y_len and y[y_line] != common:
            changes = [f'> {line}' for line in takewhile(lambda line: line != common, y[y_line:])]
            edits.append(f'{x_line}a{diff_section(y_line, changes)}\n')
            edits.extend(changes)
            y_line += len(changes)

        x_line += 1
        y_line += 1

    return ''.join(edits)