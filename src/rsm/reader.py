from ..io.reader import BinaryFileReader
from .rsm import Rsm
from pprint import pprint

class RsmReader(object):
    def __init__(self):
        self

    @staticmethod
    def from_file(path):
        with open(path, 'rb') as f:
            rsm = Rsm()
            reader = BinaryFileReader(f)
            magic = reader.read('4s')[0]
            if magic != b'GRSM':
                raise RuntimeError('Invalid file type')
            unk1 = reader.read('2B')
            unk2 = reader.read('6I')
            unk3 = reader.read('B')
            mesh_count = unk2[1]  # TODO: not confirmed (probably confirmed!)
            texture_count = reader.read('I')[0]
            for i in range(texture_count):
                texture = reader.read_fixed_length_null_terminated_string(40)
                rsm.textures.append(texture)
            for _ in range(mesh_count):
                mesh = rsm.Mesh()
                mesh.name = reader.read_fixed_length_null_terminated_string(40)
                mesh.parent_name = reader.read_fixed_length_null_terminated_string(40)
                if len(mesh.parent_name) == 1:  # TODO: something fishy about this one!
                    mesh.unknown_name = reader.read('44B')
                unk3 = reader.read('I')[0]
                print(unk3)  # maybe texture??
                print()
                mesh.floats = reader.read('13f')
                mesh.offset = reader.read('3f')
                mesh.rotation = reader.read('4f')
                mesh.scale = reader.read('3f')
                vertex_count = reader.read('I')[0]
                mesh.vertices = [reader.read('3f') for _ in range(vertex_count)]
                # Texture Coordinates
                texcoord_count = reader.read('I')[0]
                for i in range(texcoord_count):
                    texcoord = reader.read('3f')
                    mesh.texcoords.append(texcoord)
                # Faces
                face_count = reader.read('I')[0]
                # print(face_count)
                for i in range(face_count):
                    face = Rsm.Mesh.Face()
                    face.vertex_indices = reader.read('3H')
                    face.texcoord_indices = reader.read('3H')
                    face.unk1 = reader.read('4B')
                    face.unk2 = reader.read('2I')
                    mesh.faces.append(face)
                rsm.meshes.append(mesh)
                unk3 = reader.read('I')[0]  # TODO: who knows, man
            return rsm
