from collections import Counter
from heapq import heappop, heappush
from bitarray import bitarray
from array import array

class Huffman:
    class Node:
        is_leaf = False
        def __init__(self, low, high):
            self.low  = low
            self.high = high
            self.count = low.count + high.count
            
        def __lt__(self, other):
            return self.count < other.count

    class Leaf:
        is_leaf = True
        def __init__(self, char, count):
            self.char  = char
            self.count = count

        def __lt__(self, other):
            return self.count < other.count

    def __init__(self, freq=None, unicode=True):
        self.frequency = Counter(freq) if freq != None else Counter()
        self._codes= None
        self.frequency_changed = True
        self.ascii_mode = not unicode

    @property
    def array_mode(self):
        return 'B' if self.ascii_mode else 'H'

    @property
    def codes(self):
        if not self.frequency_changed:
            return self._codes

        heap = []
        for value, count in self.frequency.items():
            heappush(heap, Huffman.Leaf(value, count))
        
        while len(heap) > 1:
            low = heappop(heap)
            high = heappop(heap) 
            heappush(heap, Huffman.Node(low, high))
        
        def traverse(root, path):
            if root.is_leaf:
                yield root.char, path
            else:
                yield from traverse(root.low , path + '0')
                yield from traverse(root.high, path + '1')
        
        self._codes = dict(traverse(heap[0], bitarray(0))) \
                if not heap[0].is_leaf else dict([(heap[0].char, bitarray('0'))])
        self.frequency_changed = False
        return self._codes

    def encode(self, text):
        b = bitarray()
        b.encode(self.codes, text)
        return b

    def decode(self, b):
        return ''.join(b.decode(self.codes))

    def tofile(self, file, text):
        encoded = self.encode(text)
        meta = array(self.array_mode, [len(encoded) % 8, len(self.frequency)])
        meta.extend(self.frequency.values())
        meta.extend(map(ord, self.frequency.keys()))
        meta.tofile(file)
        encoded.tofile(file)

    def fromfile(self, file):
        meta = array(self.array_mode)
        meta.fromfile(file, 2)
        text_trim, alphabet_size = meta

        meta.fromfile(file, 2 * alphabet_size)
        alphabet, count = map(chr, meta[-alphabet_size:]), meta[2:2+alphabet_size]
        newfrequency = Counter(dict(zip(alphabet, count)))
        if newfrequency != self.frequency:
            self.frequency_changed = True
            self.frequency = newfrequency

        text = bitarray()
        text.fromfile(file)
        return self.decode(text[:-(8-text_trim)] if text_trim else text)
