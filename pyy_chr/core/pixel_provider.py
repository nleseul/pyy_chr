from abc import ABC, abstractmethod
from typing import Tuple

from events import Events
from PIL import Image

from pyy_chr.core import Buffer, PixelColorFormatException

PixelColor = Tuple[int, ...]
Coordinate = Tuple[int, int]
Size = Tuple[int, int]


class PixelProvider(ABC):
    def __init__(self) -> None:
        super().__init__()

        self.events = Events(['on_invalidated'])

    @property
    @abstractmethod
    def size(self) -> Size:
        pass

    @property
    @abstractmethod
    def color_format(self) -> str:
        pass

    @abstractmethod
    def generate_image(self, image: Image, page: int = 0) -> None:
        pass

    @abstractmethod
    def generate_point(self, point: Coordinate, page: int = 0) -> PixelColor:
        pass

    @property
    def page_count(self) -> int:
        return 1

    def _invalidate(self) -> None:
        self.events.on_invalidated(self)

    def _verify_color_format(self, color: PixelColor):
        if len(self.color_format) != len(color):
            raise PixelColorFormatException('Format {0} does not match size of data {1}.'.format(
                self.color_format, len(color)))


class WritablePixelProvider:
    @abstractmethod
    def inject_point(self, point: Coordinate, value: PixelColor, page: int = 0):
        pass


class SolidColor(PixelProvider):
    def __init__(self, size: Size, color_format: str, color: PixelColor = None):
        super().__init__()

        self._size = size
        self._color_format = color_format
        if color is None:
            self._color = (0,) * len(color_format)
        else:
            self._verify_color_format(color)
            self._color = color

    @property
    def size(self) -> Size:
        return self._size

    @property
    def color_format(self) -> str:
        return self._color_format

    @property
    def color(self) -> PixelColor:
        return self._color

    @color.setter
    def color(self, color: PixelColor) -> None:
        self._verify_color_format(color)

        self._color = color
        self._invalidate()

    def generate_image(self, image: Image, page: int = 0) -> None:
        image.paste(self._color, (0, 0) + self._size)

    def generate_point(self, point: Coordinate, page: int = 0) -> PixelColor:
        return self._color


class ValueRange(PixelProvider):
    def __init__(self, min_value: int, max_value: int, step: int = 1, wrap_value: int = None) -> None:
        super().__init__()

        self._wrap_value = wrap_value
        self._values = range(min_value, max_value, step)

    @property
    def size(self) -> Size:
        count = len(self._values)
        return (count, 1) if self._wrap_value is None else (self._wrap_value, (count // self._wrap_value))

    @property
    def color_format(self) -> str:
        return 'P'

    def generate_image(self, image: Image, page: int = 0) -> None:
        size = self.size
        for y in range(size[1]):
            for x in range(size[0]):
                image.put_pixel((x, y), self.generate_point((x, y), page))

    def generate_point(self, point: Coordinate, page: int = 0) -> PixelColor:
        return point[0] if self._wrap_value is None else point[1] * self._wrap_value + point[0]


class ColorGradient(PixelProvider):
    def __init__(self, color_format: str, min_color: PixelColor, max_color: PixelColor, points: int) -> None:
        super().__init__()

        if len(color_format) != len(min_color):
            raise PixelColorFormatException('Min color {0} does not match color format {1}!'
                                            .format(min_color, color_format))
        if len(color_format) != len(max_color):
            raise PixelColorFormatException('Max color {0} does not match color format {1}!'
                                            .format(max_color, color_format))

        self._color_format = color_format

        self._values = []
        for point_index in range(points):
            t = point_index / (points - 1)
            val = tuple(int(round(min_color[c] * (1 - t) + max_color[c] * t)) for c in range(len(min_color)))
            self._values.append(val)

    @property
    def size(self) -> Size:
        return 1, len(self._values)

    @property
    def color_format(self) -> str:
        return self._color_format

    def generate_image(self, image: Image, page: int = 0) -> None:
        for index, value in enumerate(self._values):
            image.putpixel((1, index), value)

    def generate_point(self, point: Coordinate, page: int = 0) -> PixelColor:
        return self._values[point[1]]


class BufferInterpreter(PixelProvider, WritablePixelProvider):
    def __init__(self, width: int, color_format: str, buffer: Buffer) -> None:
        super().__init__()

        self._width = width
        self._color_format = color_format
        self._buffer = buffer

        self._bytes_per_row = self._width * len(self._color_format)
        self._image = None

        self._load_buffer()

        self._buffer.events.on_changed += self._on_buffer_changed

    @property
    def size(self) -> Size:
        return self._width, len(self._buffer) // self._bytes_per_row

    @property
    def color_format(self) -> str:
        return self._color_format

    def generate_image(self, image: Image, page: int = 0) -> None:
        image.paste(self._image)

    def generate_point(self, point: Coordinate, page: int = 0) -> PixelColor:
        return self._image.getpixel(point)

    def inject_point(self, point: Coordinate, color: PixelColor, page: int = 0):
        self._verify_color_format(color)

        loc = point[1] * self._width * len(self._color_format) + point[0]
        self._buffer.write(loc, color)

    def _load_buffer(self) -> None:
        self._image = Image.frombytes(self._color_format, self.size, bytes(self._buffer.data))

    def _on_buffer_changed(self) -> None:
        self._load_buffer()
        self._invalidate()
