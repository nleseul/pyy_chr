
from PIL import Image, ImageDraw, ImageColor

class Renderer:

    def __init__(self):
        self.map_data = None
        self.tile_data = None
        self.palette_data = None
        self.map_interpreter = None
        self.tile_interpreter = None
        self.palette_interpreter = None

    '''
    def resize(self, size):
        self.width = size[0]
        self.height = size[1]

        self.tilemap = bytearray(self.width * self.height)
    '''

    def set_tile_interpreter(self, tile_interpreter):
        self.tile_interpreter = tile_interpreter

    def set_palette_interpreter(self, palette_interpreter):
        self.palette_interpreter = palette_interpreter

    def set_map_interpreter(self, map_interpreter):
        self.map_interpreter = map_interpreter

    def load_tile_data(self, tile_data):
        self.tile_data = tile_data

    def load_palette_data(self, palette_data):
        self.palette_data = palette_data

    def load_map_data(self, map_data):
        self.map_data = map_data

    '''
    def write_tiles(self, tiles, start_column, start_row):
        start_offset = start_row * self.width + start_column

        for offset in range(start_offset, start_offset + len(tiles)):
            if offset >= len(self.tilemap):
                break
            self.tilemap[offset] = tiles[offset - start_offset]


    def create_tile_preview(self):
        for tile_index in range(0, len(self.tile_data) // (8 * self.plane_depth)):
            if tile_index >= 256 or tile_index >= len(self.tilemap):
                break
            self.tilemap[tile_index] = tile_index
    '''

    def render(self):
        size = self.map_interpreter.get_size(self.map_data)

        out_img = Image.new('P', (size[0] * 8, size[1] * 8))
        out_img.info['transparency'] = 0

        palette_values = []
        for palette in range(self.palette_interpreter.num_palettes(self.palette_data)):
            for color_index in range(self.palette_interpreter.num_colors(self.palette_data)):
                palette_values += self.palette_interpreter.get_color(self.palette_data, palette, color_index)
        out_img.putpalette(palette_values)

        if self.tile_data is None:
            raise Exception('No tile data loaded!')

        cache = {}

        for row in range(0, size[1]):
            for col in range(0, size[0]):
                tile_index = self.map_interpreter.get_tile_index(self.map_data, col, row)
                if not tile_index in cache:
                    interpreted_tile = self.tile_interpreter.get_tile(self.tile_data, tile_index)
                    tile_width, tile_height = interpreted_tile.get_size()
                    tile_image = Image.new('P', (tile_width, tile_height))
                    tile_draw = ImageDraw.Draw(tile_image)
                    for x in range(tile_width):
                        for y in range(tile_height):
                            val = interpreted_tile.get((x, y))
                            palette_color = 0
                            if val != 0:
                                palette_index = self.map_interpreter.get_palette_index(self.map_data, col, row)
                                palette_color = val + palette_index * self.palette_interpreter.num_colors(self.palette_data)
                            tile_draw.point((x, y), palette_color)
                    cache[tile_index] = tile_image
                out_img.paste(cache[tile_index], (col * 8, row * 8))


        return out_img
