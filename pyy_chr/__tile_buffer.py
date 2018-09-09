class __TileBuffer:
    def __init__(self, size):
        self.size = size
        self.data = bytearray(size[0] * size[1])

    def get_size(self):
        return self.size

    def get(self, pos):
        return self.data[self.__index(pos)]

    def set(self, pos, value):
        self.data[self.__index(pos)] = value

    def __index(self, pos):
        return pos[1] * self.size[0] + pos[0]