import unittest
from src.rsm.reader import RsmReader


class TestRsmConsistency(unittest.TestCase):

    def setUp(self):
        self.rsm = RsmReader.from_file('./rsm_tests/pillar_04.rsm')

    def test_face_vertex_indices(self):
        for mesh in self.rsm.meshes:
            for face in mesh.faces:
                for texcoord_index in face.texcoord_indices:
                    self.assertLessEqual(texcoord_index, len(mesh.texcoords))
                for vertex_index in face.vertex_indices:
                    self.assertLessEqual(vertex_index, len(mesh.vertices))
                # TODO: the face should probably have a texture index?


class TestRsmReader(unittest.TestCase):

    def test_pillar(self):
        rsm = RsmReader.from_file('./rsm_tests/pillar_04.rsm')
        self.assertIsNotNone(rsm)
        self.assertEqual(len(rsm.textures), 1)
        self.assertEqual(len(rsm.meshes), 1)
        self.assertEqual(len(rsm.meshes[0].vertices), 8)
        self.assertEqual(len(rsm.meshes[0].texcoords), 16)
        self.assertEqual(len(rsm.meshes[0].faces), 10)

    def test_statue(self):
        rsm = RsmReader.from_file('./rsm_tests/prn_statue_02.rsm')
        self.assertIsNotNone(rsm)

    def test_bed(self):
        rsm = RsmReader.from_file('./rsm_tests/prt_k_bed_3.rsm')
        self.assertEqual(len(rsm.textures), 5)
        self.assertEqual(len(rsm.meshes), 2)
        self.assertIsNotNone(rsm)

    def test_export(self):
        rsm = RsmReader.from_file('./rsm_tests/prn_statue_02.rsm')
        with open('prn_statue_02.obj', 'w') as f:
            vertex_offset = 0
            texcoord_offset = 0
            for i, mesh in enumerate(rsm.meshes):
                print(i, mesh.name)
                print(mesh.offset)
                for vertex in mesh.vertices:
                    f.write('v {} {} {}\n'.format(vertex[0] + mesh.offset[0], vertex[1] + mesh.offset[1], vertex[2] + mesh.offset[2]))
                for texcoord in mesh.texcoords:
                    f.write('vt {} {}\n'.format(texcoord[1], texcoord[2]))
                for face in mesh.faces:
                    s = ' '.join('{}/{}'.format(vertex_offset + i + 1, texcoord_offset + j + 1) for i, j in zip(face.vertex_indices, face.texcoord_indices))
                    # print(face.unk1)  # TODO: this appears to be smoothing group information!!
                    f.write('f ' + s + '\n')
                vertex_offset += len(mesh.vertices)
                texcoord_offset += len(mesh.texcoords)


if __name__ == '__main__':
    unittest.main(verbosity=2)
