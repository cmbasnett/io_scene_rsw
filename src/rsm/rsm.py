
class Rsm(object):

    class Mesh(object):

        class Face(object):
            def __init__(self):
                self.vertex_indices = (0, 0, 0)
                self.texcoord_indices = (0, 0, 0)
                self.unk1 = None

        def __init__(self):
            self.vertices = []
            self.texcoords = []
            self.faces = []
            self.floats = []

    def __init__(self):
        self.textures = []
        self.meshes = []
        pass

