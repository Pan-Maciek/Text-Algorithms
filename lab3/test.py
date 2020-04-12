from huffman import Huffman

for p in ['1KB', '10KB', '100KB', '1MB']:
    with open(f"{p}.txt", "r") as file:
        x = file.read()
        with open(f"{p}.c.txt", "wb") as file:
            Huffman(x).tofile(file, x)
