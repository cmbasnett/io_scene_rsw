from typing import List


class Gnd(object):

    class Texture(object):
        def __init__(self, path: str = ''):
            self.path = path
            self.data = None

    class Tile(object):
        def __init__(self):
            self.heights = None

        def __getitem__(self, item):
            return self.heights[item]

    class Face(object):
        def __init__(self):
            self.texcoords = None
            self.texture_index = 0
            self.lighting = None

    def __init__(self, textures: List[Texture] = list(), faces: List[Face] = list(), tiles: List[Tile] = list()) -> None:
        self.textures = textures
        self.tiles = tiles
        self.faces = faces
        self.width = 0
        self.height = 0
        self.scale = (1, 1, 1)
