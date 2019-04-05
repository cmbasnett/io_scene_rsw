import unittest
from src.rsw.reader import RswReader
import math
import os


path = 'C:/Users/Colin/Desktop/data/prt_fild01.rsw'


class TestRswReader(unittest.TestCase):

    def test_reader(self):
        rsw = RswReader.from_file(path)
        for model in rsw.models:
            print(model.name)
            print(model.filename)
            print(model.scale)
        self.assertIsNotNone(rsw)


if __name__ == '__main__':
    unittest.main()
