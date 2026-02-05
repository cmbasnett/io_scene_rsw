import io
import os
import struct


class BinaryFileReader(object):
    def __init__(self, file):
        self.file = file

    def tell(self):
        return self.file.tell()

    def read(self, fmt):
        return struct.unpack(fmt, self.file.read(struct.calcsize(fmt)))

    def read_fixed_length_null_terminated_string(self, length, encoding='cp949'):
        buf = bytearray()
        for i in range(length):
            c = self.file.read(1)[0]
            if c == 0:
                self.file.seek(length - i - 1, os.SEEK_CUR)
                break
            buf.append(c)
        try:
            return buf.decode('cp949')
        except UnicodeDecodeError as e:
            return buf.decode('latin-1')
