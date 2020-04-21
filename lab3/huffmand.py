from bitarray import bitarray
from array import array
from collections import defaultdict
from dataclasses import dataclass
from math import ceil
from itertools import count

NYT = 0
class Node:
    def __init__(self, weight, order, parent, char=None):
        self.weight = weight
        self.order = order
        self.parent = parent
        self.char = char
        self.low = self.high = None
    
    @property
    def is_leaf(self):
        return self.high == None

    @property
    def code(self):
        node, code = self, bitarray()
        while node.parent != None:
            parent = node.parent
            code.append(1 if parent.high == node else 0)
            node = parent
        code.reverse()
        return code

class Tree:
    def __init__(self):
        self.root = Node(0, 512, None)

        self.leaves = {NYT: self.root}
        self.weights = defaultdict(set)
        self.weights[0].add(self.root)

        self.order = 511

    @property
    def NYT(self):
        return self.leaves[NYT]

    def add(self, letter):
        node = self.NYT

        self.leaves[NYT] = node.low = Node(0, self.order - 1, node)
        self.leaves[letter] = node.high = Node(1, self.order, node, letter)
        self.order -= 2

        self.weights[0].add(node.low)
        self.weights[1].add(node.high)

        self.update(node)

    def update(self, node):
        if node.parent != None and node.parent.weight != node.weight:
            leader = max(self.weights[node.weight], key=lambda x: x.order, default=node)
            if leader != node:
                self.swap(node, leader)

        self.weights[node.weight].remove(node)
        self.weights[node.weight + 1].add(node)
        node.weight += 1

        if node.parent != None:
            self.update(node.parent)

    def swap(self, node, leader):
        node.order, leader.order = leader.order, node.order
        node_parent, leader_parent = node.parent, leader.parent
        node._code = leader._code = None

        if node_parent.low == node: node_parent.low = leader
        else: node_parent.high = leader

        if leader_parent.low == leader: leader_parent.low = node
        else: leader_parent.high = node
        
        if node_parent != leader_parent:
            leader.parent = node_parent
            node.parent = leader_parent

def encode(text):
    tree, encoded = Tree(), bitarray()
    for letter in text:
        if letter in tree.leaves:
            encoded.extend(tree.leaves[letter].code)
            tree.update(tree.leaves[letter])
        else:
            encoded.extend(tree.NYT.code)
            encoded.frombytes(letter.encode())
            tree.add(letter)
    return encoded

def decode(bits):
    tree = Tree()
    i, current = 0, tree.root
    decoded = ''
    while i < len(bits):
        if current.is_leaf:
            if current != tree.NYT:
                letter = current.char
                tree.update(tree.leaves[letter])
            else:
                letter, offset = takeChar(bits, i)
                i += offset
                tree.add(letter)

            decoded += letter
            current = tree.root
        else:
            current = current.high if bits[i] else current.low
            i += 1

    if current.is_leaf:
        decoded += current.char
    return decoded

def tofile(file, text):
    encoded = encode(text)
    array('B', [ 8 - len(encoded) % 8 ]).tofile(file)
    encoded.tofile(file)

def takeChar(bits,i):
    for size in count(8, 8):
        try:
            letter = bits[i:i+size].tobytes().decode()
            return letter, size
        except: pass

def fromfile(file):
    def fill(to, n=-1):
        to.fromfile(file, n)
        return to
    [ excess ] = fill(array('B'), 1)
    encoded = fill(bitarray())
    encoded = encoded[:-excess] if excess != 8 else encoded # trim excess bits
    return decode(encoded)
