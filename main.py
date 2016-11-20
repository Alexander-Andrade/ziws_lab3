from bitstring import Bits, BitArray, BitStream, BitString
import pickle
import sys
import re


class JacksonCounter:

    def __init__(self, n, init_size=1):
        self.reg = BitArray(length=init_size)
        self.n = n

    def next_code(self):
        code = Bits(self.reg)
        if self.reg.all(True):
            self.reg.append('0b0')
            self.reg.set(0)
        else:
            self.reg.invert(-1)
            self.reg.ror(1)
        return code

    def get_codes(self):
        return [self.next_code() for i in range(self.n)]


class InjectiveTransform:

    def __init__(self):
        self.delim = Bits("0b01")
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

    def tables_tofile(self, f):
        pickle.dump(self.encoding_table, f)
        pickle.dump(self.decoding_table, f)

    def tables_fromfile(self, f):
        self.encoding_table = pickle.load(f)
        self.decoding_table = pickle.load(f)

    def calc_efficiency(self, text, bits):
        return len(text.encode('utf8')) * 8 / len(bits)

    def prepare_text(self, text):
        # deleting all spaces and punctuation
        text = re.sub(r'[ ,.!:-;–\n]+', '', text)
        # convert text to lowercase
        return text.lower()

    def encode(self, text):
        freq_table = self.get_freq_table(text)
        # sorting dict keys by the descending of letters frequencies
        sorted_symbols = sorted(freq_table.keys(), key=lambda key: freq_table[key], reverse=True)
        # get the list of codes for letters, the list is generated via Jackson counter
        jk = JacksonCounter(n=len(sorted_symbols), init_size=1)
        codes = jk.get_codes()
        # get encoding and decoding tables
        self.encoding_table = dict(zip(sorted_symbols, codes))
        self.decoding_table = dict(zip(codes, sorted_symbols))
        encoded_bits = BitArray()
        for ch in text:
            encoded_bits.append(self.delim+self.encoding_table[ch])
        efficiency = self.calc_efficiency(text, encoded_bits)
        return encoded_bits, efficiency

    def bits_without_delims_gen(self, bits):
        delim_pos = len(self.delim)
        gen = bits.split(self.delim)
        next(gen)
        for bits in gen:
            if bits.startswith(self.delim):
                ch_bits = bits[delim_pos:]
                if len(ch_bits):
                    yield Bits(ch_bits)

    def find_last_char_code(self, bits):
        sorted_codes = sorted(self.decoding_table.keys(), key=lambda key: len(key), reverse=True)
        for code in sorted_codes:
            if bits.startswith(code):
                return code

    def decode(self, bits):
        ch_bits_generator = self.bits_without_delims_gen(bits)
        decoded_str = ""
        for ch_bits in ch_bits_generator:
            try:
                decoded_str += self.decoding_table[ch_bits]
            except KeyError:
                code = self.find_last_char_code(ch_bits)
                decoded_str += self.decoding_table[code]
        return decoded_str


if __name__ == "__main__":
    text = ''
    # read text from file
    with open(sys.argv[1], 'r', encoding="utf8") as f:
        text = f.read()

    inj = InjectiveTransform()
    # removing punctuation and do text lowercase
    prepared_text = inj.prepare_text(text)
    encoded_bits, efficiency = inj.encode(text=prepared_text)
    print("encoding efficiency: {}".format(efficiency))
    print("encoded bit stream: {}".format(encoded_bits.bin))
    # loading encoded text to file example
    '''
    with open(sys.argv[2], 'wb') as f:
        encoded_bits.tofile(f)
    '''
    # save and load encoding, decoding tables to/from file example
    '''
    with open('tables', 'wb') as f:
        inj.tables_tofile(f)
    with open('tables', 'rb') as f:
        inj.tables_fromfile(f)
    '''

    # loading encoded text from file
    '''
    encoded_bits = Bits(filename=sys.argv[2]))
    '''
    decoded_text = inj.decode(encoded_bits)

    print("are original and decoded texts equal? : {}".format(prepared_text == decoded_text))







