from typing import List


class Gnd(object):

    class Unknown(object):
        def __init__(self):
            self.data = None

    class Texture(object):
        def __init__(self, path: str = ''):
            self.path = path
            self.data = None

    class Tile(object):
        def __init__(self):
            self.heights = None
            self.face_indices = (-1, -1, -1)

        def __getitem__(self, item):
            return self.heights[item]

    class Face(object):
        def __init__(self):
            self.texcoords = None
            self.texture_index = 0
            self.unknowns_index = 0
            self.lighting = None

        @property
        def uvs(self):
            for i in range(4):
                yield (self.texcoords[i], self.texcoords[i + 4])

    def __init__(self, textures: List[Texture] = list(), faces: List[Face] = list(), tiles: List[Tile] = list()) -> None:
        self.unknowns = []
        self.textures = textures
        self.tiles = tiles
        self.faces = faces
        self.width = 0
        self.height = 0
        self.scale = (1, 1, 1)
