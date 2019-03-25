import io
from .gnd import Gnd
from ..io.reader import BinaryFileReader


class GndReader(object):
    def __init__(self):
        pass

    @staticmethod
    def from_file(path: str):
        with open(path, 'rb') as f:
            return GndReader.from_stream(f)

    @staticmethod
    def from_stream(f: io.FileIO):
        reader = BinaryFileReader(f)
        magic = reader.read('4s')[0]
        if magic != b'GRGN':
            raise RuntimeError('Unrecognized file format.')
        gnd = Gnd()
        unk1 = reader.read('2b')  # Always seems to be 1,7 (maybe some sort of version?)
        print(unk1)
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
        gnd.scale = reader.read('3I') # TODO: this is probably lightmap scale
        # this is related, in some way, to the tile faces
        for i in range(lightmap_count):
            lightmap = Gnd.Lightmap()
            lightmap.data = reader.read('256B')
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
                # these are indices into the faces
                # there are 3 of them
                # has something to do with connectivity between tiles
                # the "unknowns" could be connective tile geometry?
                # "edge" rows have multiple invalid indices
                # "corner" ones have *all* valid indices
                # -1 indicates in invalid index
                # if k < 4000:
                #     face_unk_indices = [gnd.faces[x].unknowns_index if x != -1 else -1 for x in tile.face_indices]
                #     print(i, j, k, face_unk_indices)
                gnd.tiles.append(tile)
        return gnd
