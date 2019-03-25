import unittest
from src.gnd.reader import GndReader
from src.gnd.exporter import GndExporter
import os


path = './data/prt_monk/data/prt_monk.gnd'
# path = './data/mjolnir_10/data/mjolnir_10.gnd'

class TestGndReader(unittest.TestCase):

    def test_reader(self):
        gnd = GndReader.from_file(path)
        print(f'width: {gnd.width}')
        print(f'height: {gnd.height}')
        print(f'textures: {len(gnd.textures)}')
        print(f'faces: {len(gnd.faces)}')
        print(f'tiles: {len(gnd.tiles)}')
        print(f'lightmaps: {len(gnd.lightmaps)}')
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

    def test_face_unknown_indices(self):
        for face in self.gnd.faces:
            self.assertLessEqual(face.lightmap_index, len(self.gnd.lightmaps))


class TestGndXExporter(unittest.TestCase):

    def setUp(self):
        self.gnd = GndReader.from_file(path)

    def test_exporter(self):
        exporter = GndExporter()
        exporter.export(self.gnd, os.path.basename(path) + '.obj')
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
