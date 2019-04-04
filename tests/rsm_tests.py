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
        for node in rsm.nodes:
            print(node.name,  node.parent_name)
        self.assertIsNotNone(rsm)

    def test_export(self):
        rsm = RsmReader.from_file('./rsm_tests/fountain.rsm')
        with open('fountain.obj', 'w', encoding='utf-8') as f:
            vertex_offset = 0
            texcoord_offset = 0
            for i, node in enumerate(rsm.nodes):
                for vertex in node.vertices:
                    f.write('v {} {} {}\n'.format(vertex[0] + node.offset[0], vertex[1] + node.offset[1], vertex[2] + node.offset[2]))
                for texcoord in node.texcoords:
                    f.write('vt {} {}\n'.format(texcoord[1], texcoord[2]))
                for face in node.faces:
                    s = ' '.join('{}/{}'.format(vertex_offset + i + 1, texcoord_offset + j + 1) for i, j in zip(face.vertex_indices, face.texcoord_indices))
                    # print(face.unk1)  # TODO: this appears to be smoothing group information!!
                    f.write('f ' + s + '\n')
                vertex_offset += len(node.vertices)
                texcoord_offset += len(node.texcoords)

    def test_find_stuff(self):
        pass


if __name__ == '__main__':
    unittest.main(verbosity=2)
