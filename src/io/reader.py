import io
import os
import struct


class BinaryFileReader(object):
    def __init__(self, file: io.FileIO):
        self.file = file

    def read(self, fmt: str):
        return struct.unpack(fmt, self.file.read(struct.calcsize(fmt)))

    def read_fixed_length_null_terminated_string(self, n: int, encoding: str='euc-kr'):
        buffer = bytearray()
        for i in range(n):
            c = self.file.read(1)[0]
            if c == 0:
                self.file.seek(n - i - 1, os.SEEK_CUR)
                break
            buffer.append(c)
        return buffer.decode(encoding)
