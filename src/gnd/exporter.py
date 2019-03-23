from .gnd import Gnd


class GndPlyExporter(object):
    def __init__(self):
        pass

    @staticmethod
    def export(gnd: Gnd, path: str):
        with open(path, 'w') as f:
            f.write('ply\n')
            f.write('format ascii 1.0\n')
            # TODO: how many vertices??
            vertex_count = len(gnd.tiles) * 4
            # Vertices
            f.write(f'element vertex {vertex_count}')
            f.write('property float x')
            f.write('property float y')
            f.write('property float z')
            f.write('property float red')
            f.write('property float green')
            f.write('property float blue')
            # Faces
            face_count = len(gnd.tiles) * 2
            f.write(f'element face {face_count}')
            f.write('property list uchar int vertex_index')
            # Textures
            f.write(f'element material {len(gnd.textures)}')
            f.write('property ')

            f.write('end header')

            for i in range(gnd.height):
                for j in range(gnd.width):
                    k = (i * gnd.width) + j
                    tile = gnd.tiles[k]
                    x = i * gnd.scale[0]
                    y = j * gnd.scale[1]
                    f.write(f'{float(y)} {float(x)} {tile[0]}\n')
                    f.write(f'{float(y + gnd.scale[1])} {float(x)} {tile[1]}\n')
                    f.write(f'{float(y)} {float(x + gnd.scale[0])} {tile[2]}\n')
                    f.write(f'{float(y + gnd.scale[1])} {float(x + gnd.scale[0])} {tile[3]}\n')


class GndExporter(object):
    def __init__(self):
        pass

    @staticmethod
    def export(gnd: Gnd, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            print(gnd.scale)
            for i in range(gnd.height):
                for j in range(gnd.width):
                    k = (i * gnd.width) + j
                    tile = gnd.tiles[k]
                    x = i * gnd.scale[0]
                    y = j * gnd.scale[1]
                    f.write(f'v {float(y)} {float(x)} {tile[0]}\n')
                    f.write(f'v {float(y + gnd.scale[1])} {float(x)} {tile[1]}\n')
                    f.write(f'v {float(y)} {float(x + gnd.scale[0])} {tile[2]}\n')
                    f.write(f'v {float(y + gnd.scale[1])} {float(x + gnd.scale[0])} {tile[3]}\n')
            for i in range(gnd.height):
                for j in range(gnd.width):
                    k = (i * gnd.width) + j
                    face = gnd.faces[k]
                    for uv in face.uvs:
                        f.write(f'vt {uv[0]} {1.0 - uv[1]}\n')
            triangles_indices = ((0, 2, 1), (2, 3, 1))
            last_texture_index = -1
            for i in range(gnd.width * gnd.height):
                if gnd.faces[i].texture_index != last_texture_index:
                    texture = gnd.textures[gnd.faces[i].texture_index]
                    f.write(f'usemtl {texture.path}\n')
                    last_texture_index = gnd.faces[i].texture_index
                j = i * 4
                for triangle_indices in triangles_indices:
                    f.write(f'f {" ".join(map(lambda x: "/".join([str(j + x + 1) for _ in range(2)]), triangle_indices))}\n')

