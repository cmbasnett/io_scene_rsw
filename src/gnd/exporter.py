from .gnd import Gnd


class GndExporter(object):
    def __init__(self):
        pass

    @staticmethod
    def export(gnd: Gnd, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            scale = (8.0, 8.0, 1.0)
            for i in range(gnd.height):
                for j in range(gnd.width):
                    y = float(i * scale[0])
                    x = float(j * scale[1])
                    k = (i * gnd.width) + j
                    tile = gnd.tiles[k]
                    if tile.face_indices[0] != -1:
                        f.write(f'v {x} {y} {tile[0]}\n')
                        f.write(f'v {x + scale[1]} {y} {tile[1]}\n')
                        f.write(f'v {x} {y + scale[0]} {tile[2]}\n')
                        f.write(f'v {x + scale[1]} {y + scale[0]} {tile[3]}\n')
                    if tile.face_indices[1] != -1:
                        # TODO: Y-axis
                        adjacent_tile = gnd.tiles[k + gnd.width]
                        f.write(f'v {x} {y + scale[1]} {tile[2]}\n')
                        f.write(f'v {x + scale[0]} {y + scale[1]} {tile[3]}\n')
                        f.write(f'v {x} {y + scale[1]} {adjacent_tile[0]}\n')
                        f.write(f'v {x + scale[0]} {y + scale[1]} {adjacent_tile[1]}\n')
                    if tile.face_indices[2] != -1:
                        # TODO: this are the X-axis connective bits
                        adjacent_tile = gnd.tiles[k + 1]
                        f.write(f'v {x + scale[0]} {y} {tile[0]}\n')                      # 0
                        f.write(f'v {x + scale[0]} {y} {adjacent_tile[0]}\n')             # 1
                        f.write(f'v {x + scale[0]} {y + scale[1]} {tile[2]}\n')           # 2
                        f.write(f'v {x + scale[0]} {y + scale[1]} {adjacent_tile[2]}\n')  # 3
            for i in range(gnd.height):
                for j in range(gnd.width):
                    k = (i * gnd.width) + j
                    tile = gnd.tiles[k]
                    for face_index in filter(lambda x: x != -1, tile.face_indices):
                        face = gnd.faces[face_index]
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

