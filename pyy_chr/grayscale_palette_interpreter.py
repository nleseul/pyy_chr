
class GrayscalePaletteInterpreter:
    def __init__(self, count, skip_initial = True):
        self.count = count
        self.skip_initial = skip_initial

    def get_color(self, data, palette_index, palette_value):
        skip_offset = 1 if self.skip_initial else 0
        percent = (palette_value - skip_offset) / (self.count - 1 - skip_offset)
        color = int(percent * 255)
        color = color if color <= 255 else 255
        color = color if color >= 0 else 0
        return (color, color, color)

    def num_palettes(self, data):
        return 1

    def num_colors(self, data):
        return self.count