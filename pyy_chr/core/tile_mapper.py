from PIL import Image

from pyy_chr.core import Coordinate, PixelColor, PixelColorFormatException, PixelProvider, Size


class TileMapper(PixelProvider):
    def __init__(self, map_source: PixelProvider = None, tile_source: PixelProvider = None,
                 palette_source: PixelProvider = None) -> None:
        super().__init__()

        self._map_source = None
        self._tile_source = None
        self._palette_source = None

        self.map_source = map_source
        self.tile_source = tile_source
        self.palette_source = palette_source

        self._reset_tile_cache()

    @property
    def size(self) -> Size:
        return \
            (0, 0) if self._tile_source is None or self._map_source is None else \
            (self._tile_source.size[0] * self._map_source.size[0], self._tile_source.size[1] * self._map_source.size[1])

    @property
    def color_format(self) -> str:
        return '' if self._palette_source is None else self._palette_source.color_format

    @property
    def map_source(self) -> PixelProvider:
        return self._map_source

    @map_source.setter
    def map_source(self, map_source: PixelProvider) -> None:
        if map_source is not None and len(map_source.color_format) != 1:
            raise PixelColorFormatException('Map data format should be single-valued. Provided data has format \'{0}\'.'
                                            .format(map_source.color_format))

        if self._map_source is not None:
            self._map_source.events.on_invalidated -= self._on_invalidated
        self._map_source = map_source
        if self._map_source is not None:
            self._map_source.events.on_invalidated += self._on_invalidated

    @property
    def tile_source(self) -> PixelProvider:
        return self._tile_source

    @tile_source.setter
    def tile_source(self, tile_source: PixelProvider) -> None:
        if tile_source is not None and len(tile_source.color_format) != 1:
            raise PixelColorFormatException('Tile data format should be single-valued. Provided data has format \'{0}\'.'
                                            .format(tile_source.color_format))

        if self._tile_source is not None:
            self._tile_source.events.on_invalidated -= self._on_invalidated
        self._tile_source = tile_source
        self._reset_tile_cache()
        if self._tile_source is not None:
            self._tile_source.events.on_invalidated += self._on_invalidated

    @property
    def palette_source(self) -> PixelProvider:
        return self._palette_source

    @palette_source.setter
    def palette_source(self, palette_source: PixelProvider) -> None:
        if self.palette_source is not None:
            self._palette_source.events.on_invalidated -= self._on_invalidated
        self._palette_source = palette_source
        self._reset_tile_cache()
        if self._palette_source is not None:
            self._palette_source.events.on_invalidated += self._on_invalidated

    def generate_image(self, image: Image, page: int = 0) -> None:
        if self.tile_source is None or self.map_source is None or self.palette_source is None:
            return

        for row in range(self._map_source.size[1]):
            for col in range(self._map_source.size[0]):
                tile = self._map_source.generate_point((col, row))
                image.paste(self._get_cached_tile(tile if isinstance(tile, int) else tile[0]),
                            (col * self._tile_source.size[0], row * self._tile_source.size[1]))

    def generate_point(self, point: Coordinate, page: int = 0) -> PixelColor:
        tile_coord = point[0] // self._tile_source.size[0], point[1] // self._tile_source.size[1]
        point_offset = point[0] % self._tile_source.size[0], point[1] % self._tile_source.size[1]

        tile_image = self._get_cached_tile(self._map_source.generate_point(tile_coord)[0])
        color_index = tile_image.getpixel(point_offset)

        return self.palette_source.generate_point((0, color_index))

    def _get_cached_tile(self, tile: int) -> Image:
        if tile not in self._tile_cache:
            palette = sum([self._palette_source.generate_point((0, entry)) for entry in
                           range(self._palette_source.size[1])], ())

            tile_image = Image.new(self._tile_source.color_format, self._tile_source.size)
            tile_image.putpalette(palette)

            self._tile_source.generate_image(tile_image, tile)
            self._tile_cache[tile] = tile_image

        return self._tile_cache[tile]

    def _reset_tile_cache(self) -> None:
        self._tile_cache = {}

    def _on_invalidated(self, sender: PixelProvider) -> None:
        if sender != self._map_source:
            self._reset_tile_cache()
        self._invalidate()
