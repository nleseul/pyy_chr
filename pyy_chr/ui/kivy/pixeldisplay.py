from kivy.graphics import Color, Rectangle
from kivy.graphics.texture import Texture
from kivy.properties import BooleanProperty, BoundedNumericProperty, NumericProperty, ObjectProperty, ReferenceListProperty
from kivy.uix.widget import Widget
from PIL import Image


class PixelDisplay(Widget):
    pixel_provider = ObjectProperty()

    texture_size_x = NumericProperty(0)
    texture_size_y = NumericProperty(0)
    texture_size = ReferenceListProperty(texture_size_x, texture_size_y)

    allow_stretch = BooleanProperty(False)
    keep_ratio = BooleanProperty(True)

    page = BoundedNumericProperty(0, min=0, max=0)

    def __init__(self, **kwargs) -> None:
        super(PixelDisplay, self).__init__(**kwargs)

        self._current_provider = None
        self._current_texture = None
        self._current_image = None
        self._rectangle = None

        self.bind(pixel_provider=self._on_provider_changed)
        self.bind(page=self._on_page_changed)
        self.bind(pos=self._on_rect_changed)
        self.bind(size=self._on_rect_changed)
        self.bind(allow_stretch=self._on_rect_changed)
        self.bind(keep_ratio=self._on_rect_changed)

    def _on_rect_changed(self, *_):
        if self._rectangle is not None and self._current_texture is not None:
            pos = list(self.pos)
            size = list(self.size)

            if not self.allow_stretch:
                new_width = min(size[0], self.texture_size_x)
                new_height = min(size[1], self.texture_size_y)

                pos[0] += (size[0] - new_width) / 2
                pos[1] += (size[1] - new_height) / 2

                size[0] = new_width
                size[1] = new_height

            if self.keep_ratio:
                texture_ratio = 0 if self.texture_size_y == 0 else self.texture_size_x / self.texture_size_y
                if size[0] / size[1] > texture_ratio:
                    new_width = size[1] * texture_ratio
                    pos[0] += (size[0] - new_width) / 2
                    size[0] = new_width
                else:
                    new_height = size[0] / texture_ratio
                    pos[1] += (size[1] - new_height) / 2
                    size[1] = new_height

            pos[0] = round(pos[0])
            pos[1] = round(pos[1])

            self._rectangle.pos = pos
            self._rectangle.size = size

    def _on_provider_changed(self, *_) -> None:
        if self._current_provider is not None:
            self._current_provider.events.on_invalidated -= self._on_provider_invalidated

        self._current_provider = self.pixel_provider
        self.property('page').set_max(self, self._current_provider.page_count)
        if self.page > self._current_provider.page_count:
            self.page = self._current_provider.page_count - 1
        self._redraw()

        if self._current_provider is not None:
            self._current_provider.events.on_invalidated += self._on_provider_invalidated

    def _on_page_changed(self, *_):
        self._redraw()

    def _on_provider_invalidated(self, _: object) -> None:
        self._redraw()

    def _on_texture_reloaded(self, _: Texture) -> None:
        self._redraw()

    def _redraw(self):
        if self._current_image is None or\
                self._current_image.mode != self._current_provider.color_format or\
                self._current_image.size != self._current_provider.size:
            self._current_image = Image.new(self._current_provider.color_format, self._current_provider.size)

        if self._current_texture is None or\
                self._current_texture.size != self._current_provider.size:
            self._current_texture = Texture.create(self._current_image.size, colorfmt='RGB')
            self._current_texture.mag_filter = 'nearest'
            self._current_texture.uvpos = (0, 1)
            self._current_texture.uvsize = (1, -1)
            self._current_texture.add_reload_observer(self._on_texture_reloaded)

            self.canvas.clear()
            with self.canvas:
                Color(1, 1, 1)
                self._rectangle = Rectangle(texture=self._current_texture)

            self.texture_size_x, self.texture_size_y = self._current_texture.size
            self._on_rect_changed(None)

        if self.texture_size_x > 0 and self.texture_size_y > 0:
            self._current_provider.generate_image(self._current_image, self.page)
            self._current_texture.blit_buffer(self._current_image.convert(self._current_texture.colorfmt).tobytes())
