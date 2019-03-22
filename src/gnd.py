import os
import io
import struct
from typing import List


class BinaryFileReader(object):
    def __init__(self, file: io.FileIO):
        self.file = file

    def read(self, fmt: str):
        return struct.unpack(fmt, self.file.read(struct.calcsize(fmt)))

    def read_fixed_length_null_terminated_string(self, n: int):
        buffer = bytearray()
        for i in range(n):
            c = self.file.read(1)[0]
            if c == 0:
                self.file.seek(n - i - 1, os.SEEK_CUR)
                break
            buffer.append(c)
        return buffer.decode('euc-kr')



class Gnd(object):

    class Face(object):
        def __init__(self):
            self.texcoords = None
            self.texture_index = 0
            self.lighting = None

    def __init__(self, faces: List[Face] = list()) -> None:
        self.textures = []
        self.tiles = []
        self.faces = faces
        self.width = 0
        self.height = 0
        self.scale = (1, 1, 1)
        pass

    @staticmethod
    def from_file(path: str):
        with open(path, 'rb') as f:
            return Gnd.from_stream(f)

    @staticmethod
    def from_stream(f: io.FileIO):
        reader = BinaryFileReader(f)
        magic = reader.read('4s')[0]
        if magic != b'GRGN':
            raise RuntimeError('Unrecognized file format.')
        gnd = Gnd()
        unk1 = reader.read('2b')
        unk2 = reader.read('2I2s2I')
        gnd.width, gnd.height = unk2[0], unk2[1]
        print(unk2)
        # the first and second ones could be the tile width/height??
        texture_count = unk2[3]  # maybe??
        for i in range(texture_count):
            # TODO: it's possible that the extra bytes are uselesas and that we can just truncate them
            name = reader.read_fixed_length_null_terminated_string(32)
            unk3 = reader.read('48B')
            gnd.textures.append(name)
        unk4 = reader.read('4I')
        print(unk4)  # 9077, 8, 8, 1 ?? 8,8,1 could be dimensions of some sort
        some_count = unk4[0]  # not sure what this is, maybe lighting information?
        gnd.scale = unk4[1:]
        print('scale: ' + str(gnd.scale))
        print('some_count: {}'.format(some_count))
        # this is related, in some way, to the tile faces
        for i in range(some_count):
            unk5 = reader.read('256B')
        face_count = reader.read('I')[0]
        for i in range(face_count):
            face = Gnd.Face()
            face.texcoords = reader.read('8f') # these are probably triangle UVs (in z-winding order, hopefully)
            face.texture_index, unk7 = reader.read('2h')  # not sure what these are (maybe some sort of offset?)
            face.lighting = reader.read('4B') # not confirmed, but this is likely lighting info
            gnd.faces.append(face)
        # Tiles
        for i in range(gnd.width):
            for i in range(gnd.height):
                heights = reader.read('4f')
                gnd.tiles.append(heights)
                # values seem to bear this out as adjacent records share float values
                index = reader.read('I')[0]  # some sort of index (perhaps a triangle/vertex index?)
                unk10 = reader.read('2i')  # this may be some sort of connectivity thing??
                # print(unk10)
        return gnd


import pprint

class GndObjExporter(object):
    def __init__(self):
        pass

    def export(self, gnd: Gnd, path: str):
        print(gnd.textures)
        with open(path, 'w') as f:
            for i in range(gnd.height):
                for j in range(gnd.width):
                    k = (i * gnd.width) + j
                    tile = gnd.tiles[k]
                    x = i * gnd.scale[0]
                    y = j * gnd.scale[1]
                    f.write(f'v {float(y)} {float(x)} {tile[0]}\n')
                    f.write(f'v {float(y + gnd.scale[1])} {float(x)} {tile[1]}\n')
                    f.write(f'v {float(y)} {float(x + gnd.scale[0])} {tile[2]}\n')
                    f.write(f'v {float(y + gnd.scale[1])} {float(x + gnd.scale[0])} {tile[3]}\n')
            for i in range(gnd.height):
                for j in range(gnd.width):
                    k = (i * gnd.width) + j
                    print('*' * 10)
                    for i in range(0, 8, 2):
                        s = f'vt {" ".join(map(lambda x: str(x), gnd.faces[k].texcoords[i:i+2]))}'
                        print(s)
                        f.write(s + '\n')
            tile_count = gnd.width * gnd.height
            for i in range(tile_count):
                j = i * 4
                f.write(f'f {j + 1}/{j + 1} {j + 2}/{j + 2} {j + 3}/{j + 3}\n')
                f.write(f'f {j + 3}/{j + 3} {j + 2}/{j + 2} {j + 4}/{j + 4}\n')


def test():
    data_path = r'C:\Users\Colin\Desktop\data'
    print(data_path)
    exporter = GndObjExporter()
    for root, dirs, files in os.walk(data_path):
        for file in files:
            if file != 'prt_fild01.gnd':
                continue
            path = os.path.join(root, file)
            print(path)
            gnd = Gnd.from_file(path)
            obj_path = os.path.join(root, 'exports', os.path.basename(file) + '.obj')
            exporter.export(gnd, obj_path)


if __name__ == '__main__':
    test()
