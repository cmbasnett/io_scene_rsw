import unittest
from src.gnd.reader import GndReader
from src.gnd.exporter import GndExporter


class TestGndReader(unittest.TestCase):

    def test_reader(self):
        gnd = GndReader.from_file('./data/prt_fild01/prt_fild01.gnd')
        print(f'width: {gnd.width}')
        print(f'height: {gnd.height}')
        print(f'textures: {len(gnd.textures)}')
        print(f'faces: {len(gnd.faces)}')
        print(f'tiles: {len(gnd.tiles)}')
        print(f'unknowns: {len(gnd.unknowns)}')
        self.assertTrue(gnd is not None)


class TestGndConsistency(unittest.TestCase):

    def setUp(self):
        self.gnd = GndReader.from_file('./data/prt_fild01/prt_fild01.gnd')

    def test_face_texcoords(self):
        for face in self.gnd.faces:
            for texcoord in face.texcoords:
                self.assertTrue(0.0 <= texcoord <= 1.0)

    def test_face_texture_indices(self):
        for face in self.gnd.faces:
            self.assertLessEqual(face.texture_index, len(self.gnd.textures))

    def test_face_unknown_indices(self):
        for face in self.gnd.faces:
            self.assertLessEqual(face.unknowns_index, len(self.gnd.unknowns))


class TestGndExporter(unittest.TestCase):

    def setUp(self):
        self.gnd = GndReader.from_file('./data/prt_fild01/prt_fild01.gnd')

    def test_exporter(self):
        exporter = GndExporter()
        exporter.export(self.gnd, '/Users/colinbasnett/Desktop/prt_fild01.obj')
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
