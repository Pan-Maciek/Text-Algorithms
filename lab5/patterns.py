import numpy as np
from itertools import count
from string import ascii_letters
from dataclasses import dataclass

@dataclass
class Point:
    row: int
    col: int

@dataclass
class Range:
    top_left: Point
    bottom_right: Point

class Node:
    def __init__(self, id = 0, fail = None):
        self.children = {}
        self.id = id
        self.fail = fail

    def add(self, c, id):
        if c not in self.children:
            self.children[c] = Node(id)
        return self.children[c]

    def graft(self, text, id):
        node = self
        for c in text:
            node = node.add(c, next(id))
        return node

    def find(self, text):
        root = self
        for i, c in enumerate(text):
            if c not in root.children: 
                return root, text[i:]
            root = root.children[c]
        return root, None

class NDFA:
    def __init__(self, patterns):
        self._root = Node()
        self.accepting = []
        self.patterns_dim = []
        alphabet = set()
        id_gen = count(1)
        for pattern in patterns:
            accepting = []
            max_width = 0
            for line in pattern:
                alphabet = alphabet.union(line)
                node, rest = self._root.find(line)
                if rest: 
                    node = node.graft(rest, id_gen)
                accepting.append(node.id)
                max_width = max(max_width, len(line))
            self.accepting.append(accepting)
            self.patterns_dim.append((max_width, len(pattern)))
        
        root = self._root
        queue = []
        for c in alphabet:
            if c in root.children:
                root.children[c].fail = root
                queue.insert(0, root.children[c])
            else:
                root.children[c] = root

        while queue:
            node = queue.pop()
            for c in alphabet:
                if c in node.children:
                    next_node = node.children[c]
                    queue.insert(0, next_node)

                    x = node.fail
                    while c not in x.children:
                        x = x.fail

                    next_node.fail = x.children[c]
        
    def map(self, text):
        out = np.empty(len(text), dtype=int)
        node = root = self._root
        for i, c in enumerate(text):
            while c not in node.children and node != root:
                node = node.fail
            if c in node.children:
                node = node.children[c]
            out[i] = node.id
        return out

def editor_coords(row, col, patterns_dim):
    width, height = patterns_dim
    return Range(Point(row + 2 - height, col + 2 - width), Point(row + 1, col + 1))

def text_coords(row, col, patterns_dim):
    width, height = patterns_dim
    return Range(Point(row + 1 - height, col + 1 - width), Point(row, col))

def match(patterns, coords=editor_coords):
    line_fa = NDFA(patterns)
    dims = line_fa.patterns_dim

    def find(text):
        lines = [line_fa.map(line) for line in text.splitlines()]
        max_len = max(line.size for line in lines)

        fa = NDFA([line_fa.accepting])
        acc = fa.accepting[0]

        root = fa._root
        for col in range(max_len):
            node = root
            for row, line in enumerate(lines):
                c = line[col] if col < len(line) else 0
                while c not in node.children and node != root:
                    node = node.fail
                if c in node.children:
                    node = node.children[c]
                if node.id in acc:
                    yield coords(row, col, dims[acc.index(node.id)])
    return find