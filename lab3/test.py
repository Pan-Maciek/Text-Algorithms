from huffman import tofile, fromfile, huffman, mk_codes
from old import Huffman
import os

for p in ['1KB', '10KB', '100KB', '1MB']:
    with open(f"{p}.txt", "r") as file:
        x = file.read()
        with open(f"{p}.c.txt", "wb") as file:
            tofile(file, x)
        print(p, 1 - (os.stat(f"{p}.c.txt").st_size / os.stat(f"{p}.txt").st_size))