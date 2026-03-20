import os
import heapq


class HuffmanCoding:
    def __init__(self, path):
        self.path = path
        self.heap = []
        self.codes = {}
        self.reverse_mapping = {}
        self.root = None
        self.merge_steps = []
        self._node_id_counter = 0

    class HeapNode:
        def __init__(self, char, freq, node_id=None):
            self.char = char
            self.freq = freq
            self.left = None
            self.right = None
            self.node_id = node_id

        def __lt__(self, other):
            return self.freq < other.freq

        def __eq__(self, other):
            if other == None:
                return False
            if not isinstance(other, type(self)):
                return False
            return self.freq == other.freq

    def make_freq_dict(self, text):
        # calc freq
        frequency = {}
        for character in text:
            if not character in frequency:
                frequency[character] = 0
            frequency[character] += 1
        return frequency

    def make_heap(self, frequency):
        for key in frequency:
            node = self.HeapNode(key, frequency[key], self._next_node_id())
            heapq.heappush(self.heap, node)

    def _next_node_id(self):
        current = self._node_id_counter
        self._node_id_counter += 1
        return current

    def _node_payload(self, node):
        return {
            "id": node.node_id,
            "char": node.char,
            "freq": node.freq,
            "is_leaf": node.char is not None,
        }

    def merge_codes(self):
        while len(self.heap) > 1:
            node1 = heapq.heappop(self.heap)
            node2 = heapq.heappop(self.heap)

            merged = self.HeapNode(None, node1.freq + node2.freq, self._next_node_id())
            merged.left = node1
            merged.right = node2

            self.merge_steps.append(
                {
                    "left": self._node_payload(node1),
                    "right": self._node_payload(node2),
                    "parent": self._node_payload(merged),
                }
            )

            heapq.heappush(self.heap, merged)

    def make_codes(self):
        # Make codes for characters
        if len(self.heap) == 0:
            self.root = None
            return

        root = heapq.heappop(self.heap)
        self.root = root
        current_code = ""
        self.make_codes_helper(root, current_code)

    def _format_node(self, node):
        if node.char is None:
            return f"Internal ({node.freq})"
        return f"{repr(node.char)} ({node.freq})"

    def _show_tree_helper(self, node, prefix, is_last, edge_label):
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{edge_label}: {self._format_node(node)}")

        children = []
        if node.left is not None:
            children.append(("0", node.left))
        if node.right is not None:
            children.append(("1", node.right))

        child_prefix = prefix + ("    " if is_last else "│   ")
        for index, (label, child) in enumerate(children):
            child_is_last = index == len(children) - 1
            self._show_tree_helper(child, child_prefix, child_is_last, label)

    def show_tree(self):
        if self.root is None:
            print("Huffman tree is empty. Run compress() first.")
            return

        print("Huffman Tree (edge labels: 0=left, 1=right)")
        self._show_tree_helper(self.root, "", True, "root")

    def make_codes_helper(self, node, current_code):
        if node == None:
            return

        if node.char != None:
            code = current_code if current_code != "" else "0"
            self.codes[node.char] = code
            self.reverse_mapping[code] = node.char

        self.make_codes_helper(node.left, current_code + "0")
        self.make_codes_helper(node.right, current_code + "1")

    def get_encoded_text(self, text):
        # replace char with code and save
        encoded_text = ""
        for character in text:
            encoded_text += self.codes[character]
        return encoded_text

    def pad_encoded_text(self, encoded_text):
        # pad encoded text and return
        extra_padding = 8 - len(encoded_text) % 8
        for i in range(extra_padding):
            encoded_text += "0"

        padded_info = "{0:08b}".format(extra_padding)
        encoded_text = padded_info + encoded_text
        return encoded_text

    def get_byte_array(self, padded_encoded_text):
        # convert bits to bytes and return array
        b = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i : i + 8]
            b.append(int(byte, 2))
        return b

    def compress(self):
        self.heap = []
        self.codes = {}
        self.reverse_mapping = {}
        self.root = None
        self.merge_steps = []
        self._node_id_counter = 0

        filename, file_extension = os.path.splitext(self.path)
        output_path = filename + ".bin"
        with open(self.path, "r") as file, open(output_path, "wb") as output:
            text = file.read()

            freq = self.make_freq_dict(text)

            self.make_heap(freq)

            self.merge_codes()
            self.make_codes()

            encoded_text = self.get_encoded_text(text)
            padded_encoded_text = self.pad_encoded_text(encoded_text)

            b = self.get_byte_array(padded_encoded_text)
            output.write(bytes(b))

        print("Compressed")
        return output_path

    def remove_padding(self, bit_string):
        padded_info = bit_string[:8]
        extra_padding = int(padded_info, 2)

        bit_string = bit_string[8:]
        encoded_text = bit_string[: -1 * extra_padding]

        return encoded_text

    def decode_text(self, encoded_text):
        # decode text and return
        current_code = ""
        decoded_text = ""
        for bit in encoded_text:
            current_code += bit
            if current_code in self.reverse_mapping:
                character = self.reverse_mapping[current_code]
                decoded_text += character
                current_code = ""
        return decoded_text

    def decompress(self, input_path):
        filename, file_extension = os.path.splitext(self.path)
        output_path = filename + "_decompressed" + ".txt"
        with open(input_path, "rb") as file, open(output_path, "w") as output:
            bit_string = ""

            byte = file.read(1)
            while byte:
                byte = ord(byte)
                bits = bin(byte)[2:].rjust(8, "0")
                bit_string += bits
                byte = file.read(1)

            encoded_text = self.remove_padding(bit_string)
            decoded_text = self.decode_text(encoded_text)

            output.write(decoded_text)
        print("Decompressed")
        return output_path


if __name__ == "__main__":
    path = "file.txt"
    h = HuffmanCoding(path)

    output_path = h.compress()
    h.decompress(output_path)
