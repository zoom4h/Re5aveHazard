class RE5SaveData:
    def __init__(self):
        self.magic = bytes([0x00, 0x21, 0x11, 0x08, 0xC0, 0x4B, 0x00, 0x00])
        self.data = None

    def xor(self, data, key):
        return bytes([i^j for i,j in zip(data, key)])
    
    def open_file(self, filename):
        with open(filename, "rb") as file:
            key = self.magic
            self.data = bytes()
            while (chunk := file.read(8)):
                self.data += self.xor(chunk, key)
                key = chunk

    def save_file(self, filename):
        self.update_checksum()
        with open(filename, "wb") as file:
            key = self.magic
            i = 0
            while i <= len(self.data):
                chunk = self.data[  i : i+8 ] 
                encoded_data = self.xor(chunk, key)
                file.write(encoded_data)
                key = encoded_data
                i += 8

    def get_bytes(self, offset, length):
        return self.data[ offset : offset+length ]

    def set_bytes(self, bytes_piece, offset, length):
        self.data = self.data[ : offset ] + bytes_piece + self.data[ offset + length : ]

    def get_value(self, offset, length):
        return int.from_bytes( self.get_bytes(offset, length) , 'little' )

    def set_value(self, value, offset, length):
        bytes_piece = int.to_bytes(value, length, 'little')
        self.set_bytes(bytes_piece, offset, length)

    def get_bit(self, offset, bit_index):
        extra_offset = bit_index  // 8
        chunk = self.get_value(offset + extra_offset, 1)
        return chunk >> (bit_index - (extra_offset * 8)) & 1
    
    def set_bit(self, offset, bit_index, bit):
        extra_offset = bit_index  // 8
        chunk = self.get_value(offset + extra_offset, 1)
        prev_chunk = chunk
        mask = 1 << (bit_index - (extra_offset * 8))
        chunk |= mask
        chunk ^= (not bit) * mask
        self.set_value(chunk, offset + extra_offset, 1)

    def calculate_checksum(self):
        def chksum(offset, qty, ret):
            for i in range(offset, offset+qty*4, 4):
                val = self.get_value(i, 4)
                ret = (ret+val)%2**32
            return ret
        offset1, offset2 = 0x10, 0x3bb0
        qty1, qty2 = 0xee7, 0x5c0
        return chksum(offset2, qty2, chksum(offset1, qty1, 0))
    
    def update_checksum(self):
        self.set_value(
            self.calculate_checksum(),
            0x8,
            4
        )


if __name__ == '__main__':
    save = RE5SaveData()
    save.open_file('savedata.bin')

    off = int(input("Offset: "), 16)
    lng = int(input("Lenght: "), 10)
    val1 = save.get_value(off, lng)
    print(f'Value is {val1}')

    val2 = int(input("Set value to: "), 10)
    save.set_value(val2, off, lng)
    print(f'Changed {val1} -> {save.get_value(off, lng)} at {hex(off)}')

    save.save_file('savedata_edited.bin')