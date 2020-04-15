from collections import Counter
from heapq import heappop, heappush
from bitarray import bitarray
from array import array
from dataclasses import dataclass, field
from typing import Union
from math import ceil

@dataclass
class CmpNode:
    count: int
    def __lt__(self, other):
        return self.count < other.count

@dataclass
class Leaf(CmpNode):
    is_leaf = True
    char: chr

@dataclass
class Node(CmpNode):
    is_leaf = False
    low: CmpNode
    high: CmpNode

def huffman(frequency):
    heap, freq = [], Counter(frequency)

    for value, count in freq.items():
        heappush(heap, Leaf(count, value))
    
    while len(heap) > 1:
        low = heappop(heap)
        high = heappop(heap)
        heappush(heap, Node(low.count + high.count, low, high))

    return Node(heap[0].count, heap[0], Leaf(0, '#')) if heap[0].is_leaf else heap[0]

def mk_codes(root):
    def traverse(root, path):
        if root.is_leaf:
            yield root.char, path
        else:
            yield from traverse(root.low, path + '0')
            yield from traverse(root.high, path + '1')
    
    return dict(traverse(root, bitarray()))

def encode(text, frequency=None, tree=None, codes=None):
    codes = codes or mk_codes(tree or huffman(frequency or text))
    encoded = bitarray()
    for c in text: 
        encoded += codes[c]
    return encoded

def decode(bits, root):
    iter, out = root, ""
    for b in bits:
        iter = iter.high if b else iter.low
        if iter.is_leaf:
            out += iter.char
            iter = root
    return out

def tofile(file, text, frequency=None, tree=None, codes=None):
    tree = tree or huffman(frequency or text) 

    # encoding tree shape (0 - branch; 1 - leaf)
    alphabet, shape = '', bitarray() 
    def encode_tree(root):
        nonlocal alphabet, shape
        if root.is_leaf:
            alphabet += root.char
            shape += '1'
        else:
            shape += '0'
            encode_tree(root.low)
            encode_tree(root.high)

    encode_tree(tree)

    alphabet_bytes =  array('B', alphabet.encode())
    encoded = encode(text, frequency, tree, codes)
    array('H', [ 
        len(alphabet_bytes), 
        (ceil(len(shape) / 8) << 3) | (8 - len(encoded) % 8) 
    ]).tofile(file)
    alphabet_bytes.tofile(file)
    shape.tofile(file)
    encoded.tofile(file)

def fromfile(file):
    def fill(to, n=-1):
        to.fromfile(file, n)
        return to

    alphabet_bytes_size, encoded_shape_excess = fill(array('H'), 2)
    excess = encoded_shape_excess & 0b111
    shape_bytes = encoded_shape_excess >> 3

    alphabet_it = iter(fill(array('B'), alphabet_bytes_size).tobytes().decode())
    shape_it = iter(fill(bitarray(), shape_bytes))

    def parse_tree():
        return Leaf(0, next(alphabet_it)) if next(shape_it) \
            else Node(0, parse_tree(), parse_tree())

    root = parse_tree()
    encoded = fill(bitarray())
    encoded = encoded[:-excess] if excess != 8 else encoded # trim excess bits
    return decode(encoded, root)