
from PIL import Image, ImageDraw, ImageColor

class Renderer:
    
    def __init__(self):
        self.resize((16, 16))
        self.plane_depth = 2
        
        self.tile_data = None
        
    def resize(self, size):
        self.width = size[0]
        self.height = size[1]
        
        self.tilemap = bytearray(self.width * self.height)
        
    def load_tile_data(self, tile_data):
        self.tile_data = tile_data
        
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
        
    def render(self):
        out_img = Image.new('P', [self.width * 8, self.height * 8])
        out_img.info['transparency'] = 0
        out_img.putpalette([
            0, 0, 128,
            0, 0, 0,
            128, 128, 128,
            255, 255, 255
        ])
        
        if self.tile_data is None:
            raise Exception('No tile data loaded!')
            
        if self.tilemap is None:
            raise Exception('No tilemap created!')
        
        draw = ImageDraw.Draw(out_img)
        tile_data_size = 8 * self.plane_depth

        for row in range(0, self.height):
            for col in range(0, self.width):
            
                tilemap_offset = row * self.width + col
                if tilemap_offset >= len(self.tilemap):
                    break
            
                tile_index = self.tilemap[tilemap_offset]
                tile_data_offset = tile_index * tile_data_size
                
                tile_bytes = self.tile_data[tile_data_offset:tile_data_offset + tile_data_size]
                self.draw_tile(draw, tile_bytes, self.plane_depth, col * 8, row * 8)
        
        return out_img
        
        
    def draw_tile(self, draw, tile_bytes, plane_depth, start_x, start_y):
        for y in range(0, 8):
            for x in range(0, 8):
                pos = (start_x + x, start_y + y)
                val = 0
                for plane in range(0, plane_depth):
                    bit = (tile_bytes[y * plane_depth + plane] >> (7 - x)) & 1
                    val |= bit << plane
                if val != 0:
                    draw.point(pos, val)
            
    def map_palette(self, palette_index):
        gray = (palette_index - 1) * 128
        return (gray, gray, gray)