from io import BytesIO
from PIL import Image

from pyy_chr.core import Buffer, Coordinate, PixelColor, PixelProvider, Size


class BitplaneInterpreter(PixelProvider):
    def __init__(self, buffer: Buffer, interleaved_row_count: int, layer_count: int):
        super().__init__()

        if interleaved_row_count + layer_count > 8:
            raise Exception('No more than 8 bits total are supported! interleaved={0}, layers={1}'
                            .format(interleaved_row_count, layer_count))

        self._interleaved_row_count = interleaved_row_count
        self._layer_count = layer_count
        self._buffer = buffer

        self._bytes_per_layer = 8 * self._interleaved_row_count
        self._bytes_per_page = self._bytes_per_layer * self._layer_count

        self._image = None

        self._process_buffer()

    @property
    def size(self) -> Size:
        return 8, 8

    @property
    def color_format(self) -> str:
        return 'P'

    @property
    def page_count(self) -> int:
        return len(self._buffer) // self._bytes_per_page

    def generate_image(self, image: Image, page: int = 0) -> None:
        image.paste(self._image.crop((0, page * self.size[1], self.size[0], page * self.size[1] + self.size[1])))

    def generate_point(self, point: Coordinate, page: int = 0) -> PixelColor:
        return self._image.getpixel((point[0], point[1] + page * self.size[1]))

    def _process_buffer(self):
        in_data = BytesIO(self._buffer.data)
        out_data = BytesIO()

        while True:
            page_data = in_data.read(self._bytes_per_page)
            if len(page_data) < self._bytes_per_page:
                break

            for y in range(8):
                for x in range(8):
                    bitplane = 0
                    val = 0

                    for layer in range(self._layer_count):
                        layer_start = layer * self._interleaved_row_count * 8
                        for interleave in range(self._interleaved_row_count):
                            bit = (page_data[layer_start + y * self._interleaved_row_count + interleave] >> (7 - x)) & 1
                            val |= bit << bitplane
                            bitplane += 1

                    out_data.write(val.to_bytes(1, byteorder='big'))

        self._image = Image.frombytes(self.color_format, (self.size[0], self.size[1] * self.page_count),
                                      out_data.getvalue())
