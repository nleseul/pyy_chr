class NesMapInterpreter:
    def __init__(self, size):
        self.size = size

    def get_size(self, data):
        return self.size

    def get_tile_index(self, data, col, row):
        map_offset = row * self.size[0] + col

        return data[map_offset] if map_offset < len(data) else 0

    def get_palette_index(self, data, col, row):
        block_col = col // 2
        block_row = row // 2


        palette_index = self.size[0] * self.size[1] + (block_row // 2) * -(-self.size[0] // 4) + block_col // 2
        if palette_index >= len(data):
            return 0

        palette_bit_shift = 0 if block_col % 2 == 0 else 2
        palette_bit_shift += 0 if block_row % 2 == 0 else 4

        palette_value = (data[palette_index] & (0x3 << palette_bit_shift)) >> palette_bit_shift

        return palette_value
