from events import Events
from typing import Callable, Sequence


class Buffer:
    class BufferWriter:
        def __init__(self, on_done: Callable, max_length: int) -> None:
            self._on_done = on_done
            self._max_length = max_length

            self._writes = []

        def write(self, start_pos: int, data: Sequence[int]) -> 'Buffer.BufferWriter':
            if start_pos < 0 or start_pos + len(data) > self._max_length:
                raise IndexError('Data range {0}-{1} is out of range for a buffer of length {2}.'.format(
                    start_pos, start_pos + len(data), self._max_length))

            self._writes.append((start_pos, bytes(data)))
            return self

        def end_write(self) -> None:
            self._on_done(self._writes)

            self._writes = None
            self._on_done = None

    def __init__(self, data: Sequence[int]) -> None:
        self._data = data

        self._current_writer = None

        self.events = Events(['on_changed'])

    def __getitem__(self, value):
        return self._data[value]

    def __len__(self):
        return len(self._data)

    @property
    def data(self):
        return self._data

    def begin_write(self) -> BufferWriter:
        if self._current_writer is not None:
            raise Exception('Write already in progress!')
        return Buffer.BufferWriter(self._on_write_done, len(self._data))

    def write(self, start_pos: int, data: Sequence[int]) -> None:
        self.begin_write().write(start_pos, data).end_write()

    def _on_write_done(self, writes) -> None:
        for write_item in writes:
            self._data[write_item[0]:write_item[0] + len(write_item[1])] = write_item[1]
        self.events.on_changed()
