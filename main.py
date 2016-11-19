from bitarray import bitarray

import numpy as np
import sys
import re


class JacksonCounter:

    def __init__(self, n, init_reg_size=1, ):
        self.reg = bitarray(init_reg_size)
        self.reg.setall(False)
        self.n = n
        self.i = 0

    def __invert_reg_bit(self, i):
        self.reg[i] = True if self.reg[i] == False else True

    def __next_code(self):
        code = self.reg.copy()
        if self.i < len(self.reg):
            self.__invert_reg_bit(self.i)
            self.i += 1
        else:
            self.reg.append(False)
            self.reg.setall(False)
            self.i = 0
        return code

    def get_codes(self):
        codes = [self.__next_code() for i in range(self.n)]
        return codes


class InjectiveTransform:

    def __init__(self):
        self.delim = bitarray("01")
        self.encoding_table = None
        self.decoding_table = None

    def get_freq_table(self, text):
        freq_table = dict()
        for ch in text:
            if freq_table.get(ch):
                freq_table[ch] += 1
            else:
                freq_table[ch] = 1
        return freq_table

    def calc_efficiency(self, text, bits):
        return len(text.encode('utf8')) * 8 / len(bits)

    def encode(self, text):
        # deleting all spaces and punctuation
        text = re.sub(r'[ ,.!:-;–\n]+', '', text)
        # convert text to lowercase
        text = text.lower()
        freq_table = self.get_freq_table(text)
        # sorting dict keys by the descending of letters frequencies
        sorted_symbols = sorted(freq_table.keys(), key=lambda key: freq_table[key], reverse=True)
        jk = JacksonCounter(len(sorted_symbols), 1)
        codes = jk.get_codes()
        codes_stings = map(lambda code: code.to01(), codes)
        self.encoding_table = dict(zip(sorted_symbols, codes))
        self.decoding_table = dict(zip(codes_stings, sorted_symbols))
        encoded_bits = bitarray()
        for ch in text:
            encoded_bits.extend(self.delim+self.encoding_table[ch])
        efficiency = self.calc_efficiency(text, encoded_bits)
        return encoded_bits, efficiency

    def decode(self, bits):
        s = bits.to01()
        encoded_letters = s.split(self.delim.to01())[1:-1]
        decoded_str = ""
        for en_l in encoded_letters:
            decoded_str += self.decoding_table[en_l]
        return decoded_str


if __name__ == "__main__":
    with open(sys.argv[1], 'r', encoding="utf8") as f:
        text = f.read()
        inj = InjectiveTransform()
        encoded_bits, efficiency = inj.encode(text=text)
        print("encoding efficiency: {}".format(efficiency))
        out_file = open(sys.argv[2], 'wb')
        encoded_bits.tofile(out_file)
        decoded = inj.decode(encoded_bits)







