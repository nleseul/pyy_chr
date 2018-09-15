class StandardMapInterpreter:
    def __init__(self, size):
        self.size = size

    def get_size(self, data):
        return self.size

    def get_tile_index(self, data, col, row):
        map_offset = row * self.size[0] + col

        return data[map_offset] if map_offset < len(data) else 0

    def get_palette_index(self, data, col, row):
        return 0
