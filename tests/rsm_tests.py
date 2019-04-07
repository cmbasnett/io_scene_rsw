import unittest
from src.rsm.reader import RsmReader


class TestRsmConsistency(unittest.TestCase):

    def setUp(self):
        self.rsm = RsmReader.from_file('./rsm_tests/pillar_04.rsm')

    def test_face_vertex_indices(self):
        for node in self.rsm.nodes:
            for face in node.faces:
                for texcoord_index in face.texcoord_indices:
                    self.assertLessEqual(texcoord_index, len(node.texcoords))
                for vertex_index in face.vertex_indices:
                    self.assertLessEqual(vertex_index, len(node.vertices))
                # TODO: the face should probably have a texture index?


class TestRsmReader(unittest.TestCase):

    def test_pillar(self):
        rsm = RsmReader.from_file('./rsm_tests/pillar_04.rsm')
        self.assertIsNotNone(rsm)
        self.assertEqual(len(rsm.textures), 1)
        self.assertEqual(len(rsm.nodes), 1)
        self.assertEqual(len(rsm.nodes[0].vertices), 8)
        self.assertEqual(len(rsm.nodes[0].texcoords), 16)
        self.assertEqual(len(rsm.nodes[0].faces), 10)

    def test_statue(self):
        rsm = RsmReader.from_file('./rsm_tests/prn_statue_02.rsm')
        self.assertIsNotNone(rsm)

    def test_bed(self):
        rsm = RsmReader.from_file('./rsm_tests/prt_k_bed_3.rsm')
        self.assertIsNotNone(rsm)
        self.assertEqual(len(rsm.textures), 5)
        self.assertEqual(len(rsm.nodes), 5)

    def test_dish(self):
        rsm = RsmReader.from_file('./rsm_tests/dish_01.rsm')
        self.assertIsNotNone(rsm)

    def test_fountain(self):
        rsm = RsmReader.from_file('./rsm_tests/fountain.rsm')
        self.assertIsNotNone(rsm)

    def test_tree(self):
        rsm = RsmReader.from_file(r'C:/Users/Colin/Desktop/data/model/나무잡초꽃/나무02.rsm')
        for node in rsm.nodes:
            print(node.some_matrix) # not sure what this is tbh
            print(node.offset)  # the "main" model needs to use this offset
            print(node.offset_)
            print(node.scale)
        self.assertIsNotNone(rsm)

    def test_bush(self):
        rsm = RsmReader.from_file(r'./rsm_tests/덤불02.rsm')
        node = rsm.nodes[0]
        print(dir(node))
        print(node.some_matrix)
        print(node.rotation)
        print(node.offset)
        print(node.offset_)
        print(node.scale)
        return self.assertIsNotNone(rsm)


if __name__ == '__main__':
    unittest.main(verbosity=2)
