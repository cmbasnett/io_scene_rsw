import unittest
from src.gnd.reader import GndReader
from PIL import Image
import math
import os


# path = './data/prt_monk/data/prt_monk.gnd'
# path = './data/mjolnir_10/data/mjolnir_10.gnd'
path = './data/prt_fild01/prt_fild01.gnd'


class TestGndReader(unittest.TestCase):

    def test_reader(self):
        gnd = GndReader.from_file(path)
        print('width: {}'.format(gnd.width))
        print('height: {}'.format(gnd.height))
        print('textures: {}'.format(len(gnd.textures)))
        print('faces: {}'.format(len(gnd.faces)))
        print('tiles: {}'.format(len(gnd.tiles)))
        print('lightmaps: {}'.format(len(gnd.lightmaps)))
        self.assertTrue(gnd is not None)


class TestGndConsistency(unittest.TestCase):

    def setUp(self):
        self.gnd = GndReader.from_file(path)

    def test_face_texcoords(self):
        for face in self.gnd.faces:
            for texcoord in face.texcoords:
                self.assertTrue(0.0 <= texcoord <= 1.0)

    def test_face_texture_indices(self):
        for face in self.gnd.faces:
            self.assertLessEqual(face.texture_index, len(self.gnd.textures))

    def test_face_lightmap_indices(self):
        for face in self.gnd.faces:
            self.assertLessEqual(face.lightmap_index, len(self.gnd.lightmaps))

    def test_lightmaps(self):
        # TODO: export lightmap to a big lightmap atlas
        lightmap_count = len(self.gnd.lightmaps)
        dim = int(math.ceil(math.sqrt(lightmap_count * 64) / 8) * 8)
        num_dim = dim / 8
        image = Image.new('L', (dim, dim))
        for i, lightmap in enumerate(self.gnd.lightmaps):
            print(lightmap.color)
        image.save('lightmap.bmp')
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
