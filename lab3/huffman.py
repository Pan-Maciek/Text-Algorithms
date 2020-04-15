from collections import Counter
from heapq import heappop, heappush
from bitarray import bitarray
from array import array
from dataclasses import dataclass, field
from typing import Union

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
    freq = frequency or Counter(text)
    alphabet_bytes =  array('B', (''.join(freq.keys())).encode())
    encoded = encode(text, freq, tree, codes)
    array('H', [ len(alphabet_bytes), len(encoded) % 8 ]).tofile(file)
    alphabet_bytes.tofile(file)
    array('H', freq.values()).tofile(file)

    encoded.tofile(file)

def fromfile(file):
    metadata = array('H')
    metadata.fromfile(file, 2)
    alphabet_bytes_size, encoded_excess = metadata

    alphabet_bytes = array('B')
    alphabet_bytes.fromfile(file, alphabet_bytes_size)
    alphabet = alphabet_bytes.tobytes().decode()
    frequency = array('H')
    frequency.fromfile(file, len(alphabet))

    frequency = Counter(dict(zip(alphabet, frequency)))
    encoded = bitarray()
    encoded.fromfile(file)
    encoded = encoded[:-encoded_excess] if encoded_excess else encoded

    return decode(encoded, huffman(frequency))