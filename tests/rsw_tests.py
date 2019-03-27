import unittest
from src.rsw.reader import RswReader
import math
import os


path = './rsw_tests/in_hunter.rsw'


class TestRswReader(unittest.TestCase):

    def test_reader(self):
        rsw = RswReader.from_file(path)
        self.assertIsNotNone(rsw)


if __name__ == '__main__':
    unittest.main()
