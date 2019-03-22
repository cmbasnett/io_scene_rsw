import unittest
from src.gnd.reader import GndReader
from src.gnd.exporter import GndExporter


class TestGndReader(unittest.TestCase):
    def test_bad_file(self):
        self.assertTrue(True)

    def test_reader(self):
        gnd = GndReader.from_file('./data/prt_fild01/prt_fild01.gnd')
        self.assertTrue(gnd is not None)

    def test_exporter(self):
        gnd = GndReader.from_file('./data/prt_fild01/prt_fild01.gnd')
        exporter = GndExporter()
        exporter.export(gnd, '/Users/colinbasnett/Desktop/prt_fild01.obj')
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
