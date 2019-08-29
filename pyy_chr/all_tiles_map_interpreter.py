class AllTilesMapInterpreter:
    def __init__(self, size):
        self.size = size

    def get_size(self, data):
        return self.size

    def get_tile_index(self, data, col, row):
        return row * self.size[0] + col

    def get_palette_index(self, data, col, row):
        return 0
