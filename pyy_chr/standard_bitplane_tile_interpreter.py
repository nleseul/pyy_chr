from .__tile_buffer import __TileBuffer as TileBuffer
print(dir(TileBuffer))

class StandardBitplaneTileInterpreter:
    def __init__(self, interleaved_count, layered_count):
        self.interleaved_count = interleaved_count
        self.layered_count = layered_count

    def get_tile(self, data, tile_index):
        size = self.interleaved_count * self.layered_count * 8
        start = tile_index * size

        tile_data = data[start:start + size]

        out_data = TileBuffer((8, 8))

        for x in range(8):
            for y in range(8):
                bitplane = 0
                val = 0

                for layer in range(self.layered_count):
                    layer_start = layer * self.interleaved_count * 8
                    for interleave in range(self.interleaved_count):
                        bit = (tile_data[layer_start + y * self.interleaved_count + interleave] >> (7 - x)) & 1
                        val |= bit << bitplane
                        bitplane += 1

                out_data.set((x, y), val)

        return out_data