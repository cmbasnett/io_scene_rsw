import io
from .gnd import Gnd
from ..io.reader import BinaryFileReader
from itertools import islice


# https://stackoverflow.com/a/22045226/2209008
def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


class GndReader(object):
    def __init__(self):
        pass

    @staticmethod
    def from_file(path):
        with open(path, 'rb') as f:
            return GndReader.from_stream(f)

    @staticmethod
    def from_stream(f):
        reader = BinaryFileReader(f)
        magic = reader.read('4s')[0]
        if magic != b'GRGN':
            raise RuntimeError('Unrecognized file format.')
        gnd = Gnd()
        unk1 = reader.read('2b')  # Always seems to be 1,7 (maybe some sort of version?)
        unk2 = reader.read('2I2s2I')
        gnd.width, gnd.height = unk2[0], unk2[1]
        # the first and second ones could be the tile width/height??
        texture_count = unk2[3]  # maybe?
        for i in range(texture_count):
            texture = Gnd.Texture()
            texture.path = reader.read_fixed_length_null_terminated_string(32)
            texture.data = reader.read('48B')
            gnd.textures.append(texture)
        lightmap_count = reader.read('I')[0]
        gnd.scale = reader.read('3I')  # TODO: this is probably lightmap scale
        # this is related, in some way, to the tile faces
        for i in range(lightmap_count):
            lightmap = Gnd.Lightmap()
            lightmap.luminosity = reader.read('64B')
            lightmap.color = list(chunk(reader.read('192B'), 3))
            gnd.lightmaps.append(lightmap)
        face_count = reader.read('I')[0]
        for i in range(face_count):
            face = Gnd.Face()
            face.texcoords = reader.read('8f')
            face.texture_index = reader.read('H')[0]
            face.lightmap_index = reader.read('H')[0]
            face.lighting = reader.read('4B')  # not confirmed, but this is likely vertex lighting info
            gnd.faces.append(face)
        # Tiles
        for i in range(gnd.width):
            for j in range(gnd.height):
                k = i * gnd.height + j
                tile = Gnd.Tile()
                tile.heights = reader.read('4f')
                tile.face_indices = reader.read('3i')
                gnd.tiles.append(tile)
        return gnd
