from .gnd import Gnd


class GndExporter(object):
    def __init__(self):
        pass

    @staticmethod
    def export(gnd: Gnd, path: str):
        with open(path, 'w') as f:
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
                    for l in range(0, 4):
                        face = gnd.faces[k]
                        print(face.texcoords)
                        s = f'vt {face.texcoords[l]} {face.texcoords[l + 4]}\n'
                        f.write(s)
            tile_count = gnd.width * gnd.height
            for i in range(tile_count):
                j = i * 4
                f.write(f'f {j + 1}/{j + 1} {j + 2}/{j + 2} {j + 3}/{j + 3}\n')
                f.write(f'f {j + 3}/{j + 3} {j + 2}/{j + 2} {j + 4}/{j + 4}\n')

