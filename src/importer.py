import os
import bpy
import bpy_extras
import bmesh
import math
# import os
# import math
# from mathutils import Vector, Matrix, Quaternion
from bpy.props import StringProperty, BoolProperty, FloatProperty
from .gnd.reader import GndReader
from .rsm.reader import RsmReader
from .rsw.reader import RswReader


def explode_path(p):
    p = os.path.normpath(p)
    p = p.split(os.sep)
    return p


def implode_path(p):
    return os.sep.join(p)


def rtrim_path_until(p, dir):
    parts = explode_path(p)
    try:
        i = list(reversed(parts)).index(dir)
        if i == 0:
            return p
    except ValueError:
        return ''
    return implode_path(parts[0:-i])


def get_data_path(p):
    data_path = rtrim_path_until(p, 'data')
    if data_path == '':
        return os.path.dirname(p)
    return data_path


class GndImportOperator(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = 'io_scene_rsw.gnd_import'  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = 'Import Ragnarok Online GND'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    filename_ext = ".gnd"

    filter_glob = StringProperty(
        default="*.gnd",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    @staticmethod
    def import_gnd(filepath):
        gnd = GndReader.from_file(filepath)
        name = os.path.splitext(os.path.basename(filepath))[0]
        mesh = bpy.data.meshes.new(name)
        mesh_object = bpy.data.objects.new(name, mesh)
        directory_name = os.path.dirname(filepath)

        ''' Create materials. '''
        materials = []
        for i, texture in enumerate(gnd.textures):
            texture_path = texture.path
            material = bpy.data.materials.new(texture_path)
            material.diffuse_intensity = 1.0
            material.specular_intensity = 0.0
            materials.append(material)

            ''' Create texture. '''
            texture = bpy.data.textures.new(texture_path, type='IMAGE')
            data_path = get_data_path(directory_name)

            texpath = os.path.join(data_path, 'texture', texture_path)
            try:
                texture.image = bpy.data.images.load(texpath, check_existing=True)
            except RuntimeError:
                pass

            texture_slot = material.texture_slots.add()
            texture_slot.texture = texture

        '''
        Generate light map image.
        '''
        lightmap_size = int(math.ceil(math.sqrt(len(gnd.lightmaps) * 64) / 8) * 8)
        lightmap_tiles_per_dimension = lightmap_size / 8
        pixel_count = lightmap_size * lightmap_size
        pixels = [0.0] * pixel_count * 4
        for i, lightmap in enumerate(gnd.lightmaps):
            x, y = int(i % lightmap_tiles_per_dimension) * 8, int(i / lightmap_tiles_per_dimension) * 8
            for y2 in range(8):
                for x2 in range(8):
                    lum = lightmap.luminosity[y2 * 8 + x2]
                    i = int(((y + y2) * lightmap_size) + (x + x2)) * 4
                    r = lum / 255.0
                    pixels[i + 0] = r
                    pixels[i + 1] = r
                    pixels[i + 2] = r
                    pixels[i + 3] = 1.0
        lightmap_image = bpy.data.images.new('lightmap', lightmap_size, lightmap_size)
        lightmap_image.pixels = pixels

        bm = bmesh.new()
        bm.from_mesh(mesh)

        scale = 10

        for y in range(gnd.height):
            for x in range(gnd.width):
                tile_index = y * gnd.width + x
                tile = gnd.tiles[tile_index]
                if tile.face_indices[0] != -1:  # +Z
                    bm.verts.new(((x + 0) * scale, (y + 0) * scale, tile[0]))
                    bm.verts.new(((x + 1) * scale, (y + 0) * scale, tile[1]))
                    bm.verts.new(((x + 1) * scale, (y + 1) * scale, tile[3]))
                    bm.verts.new(((x + 0) * scale, (y + 1) * scale, tile[2]))
                if tile.face_indices[1] != -1:  # +Y
                    adjacent_tile = gnd.tiles[tile_index + gnd.width]
                    bm.verts.new(((x + 0) * scale, (y + 1) * scale, tile[2]))
                    bm.verts.new(((x + 1) * scale, (y + 1) * scale, tile[3]))
                    bm.verts.new(((x + 1) * scale, (y + 1) * scale, adjacent_tile[1]))
                    bm.verts.new(((x + 0) * scale, (y + 1) * scale, adjacent_tile[0]))
                if tile.face_indices[2] != -1:  # +X
                    adjacent_tile = gnd.tiles[tile_index + 1]
                    bm.verts.new(((x + 1) * scale, (y + 1) * scale, tile[3]))
                    bm.verts.new(((x + 1) * scale, (y + 0) * scale, tile[1]))
                    bm.verts.new(((x + 1) * scale, (y + 0) * scale, adjacent_tile[0]))
                    bm.verts.new(((x + 1) * scale, (y + 1) * scale, adjacent_tile[2]))

        bm.verts.ensure_lookup_table()

        vertex_offset = 0
        for y in range(gnd.height):
            for x in range(gnd.width):
                tile_index = y * gnd.width + x
                tile = gnd.tiles[tile_index]
                for face_index in filter(lambda x: x >= 0, tile.face_indices):
                    face = gnd.faces[face_index]
                    vertex_indices = [vertex_offset + i for i in range(4)]
                    bmface = bm.faces.new([bm.verts[x] for x in vertex_indices])
                    bmface.material_index = face.texture_index
                    vertex_offset += 4

        bm.faces.ensure_lookup_table()

        bm.to_mesh(mesh)

        ''' Add materials to mesh. '''
        uv_texture = mesh.uv_textures.new()
        lightmap_uv_texture = mesh.uv_textures.new()
        for material in materials:
            ''' Create UV map. '''
            mesh.materials.append(material)
            material.texture_slots[0].uv_layer = uv_texture.name
            # TODO: add the lightmap to a texture slot

        '''
        Assign texture coordinates.
        '''
        uv_texture = mesh.uv_layers[0]
        lightmap_uv_layer = mesh.uv_layers[1]
        lightmap_tiles = math.pow(lightmap_tiles_per_dimension, 2)
        for face_index, face in enumerate(gnd.faces):
            uvs = list(face.uvs)
            '''
            Since we are adding quads and not triangles, we need to
            add the UVs in quad clockwise winding order.
            '''
            uvs = [uvs[x] for x in [0, 1, 3, 2]]
            for i, uv in enumerate(uvs):
                # UVs have to be V-flipped
                uv = uv[0], 1.0 - uv[1]
                uv_texture.data[face_index * 4 + i].uv = uv
            # TODO: need to know what the lightmap dim is
            x1 = (face.lightmap_index % lightmap_tiles)
            y1 = (face.lightmap_index / lightmap_tiles)
            x2 = x1 + (1.0 / lightmap_tiles_per_dimension)
            y2 = y1 + (1.0 / lightmap_tiles_per_dimension)
            lightmap_uvs = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
            for i, uv in enumerate(lightmap_uvs):
                # TODO: maybe flip
                print((i, uv))
                lightmap_uv_layer.data[face_index * 4 + i].uv = uv

        bpy.context.scene.objects.link(mesh_object)
        return mesh_object

    def execute(self, context):
        GndImportOperator.import_gnd(self.filepath)
        return {'FINISHED'}

    @staticmethod
    def menu_func_import(self, context):
        self.layout.operator(GndImportOperator.bl_idname, text='Ragnarok Online GND (.gnd)')


class RswImportOperator(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = 'io_scene_rsw.rsw_import'  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = 'Import Ragnarok Online RSW'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    filename_ext = ".rsw"

    filter_glob = StringProperty(
        default="*.rsw",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    data_path = StringProperty(
        default='',
        maxlen=255,
        subtype='DIR_PATH'
    )

    should_import_gnd = BoolProperty(default=True)
    should_import_models = BoolProperty(default=True)

    def execute(self, context):
        # Load the RSW file
        rsw = RswReader.from_file(self.filepath)

        # Find the data path.
        dirname = os.path.dirname(self.filepath)
        data_path = get_data_path(dirname)

        # TODO: create an EMPTY object that is the RSW parent object

        # Load the GND file and import it into the scene.
        if self.should_import_gnd:
            gnd_path = os.path.join(data_path, rsw.gnd_file)
            try:
                gnd_object = GndImportOperator.import_gnd(gnd_path)
            except FileNotFoundError:
                self.report({'ERROR'}, 'GND file ({}) could not be found in directory ({}).'.format(rsw.gnd_file, data_path))
                return {'CANCELLED'}

        if self.should_import_models:
            # Load up all the RSM files and import them into the scene.
            models_path = os.path.join(data_path, 'models')
            for rsw_model in rsw.models:
                rsm_path = os.path.join(models_path, rsw_model.filename)
                try:
                    model_object = RsmImportOperator.import_rsm(rsm_path)
                except FileNotFoundError:
                    self.report({'ERROR'}, 'RSM file ({}) could not be found in directory ({}).'.format(rsw_model.filename, models_path))
                    return {'CANCELLED'}
                # Rename the model
                # TODO: move this guy accordingly!
                # Parent the model to the GND or some sort of super-object
        return {'FINISHED'}

    @staticmethod
    def menu_func_import(self, context):
        self.layout.operator(RswImportOperator.bl_idname, text='Ragnarok Online RSW (.rsw)')


class RsmImportOperator(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = 'io_scene_rsw.rsm_import'  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = 'Import Ragnarok Online RSM'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    filename_ext = ".rsm"

    filter_glob = StringProperty(
        default="*.rsm",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    @staticmethod
    def import_rsm(filepath):
        rsm = RsmReader.from_file(filepath)
        dirname = os.path.dirname(filepath)
        materials = []
        for texture_path in rsm.textures:
            material = bpy.data.materials.new(texture_path)
            material.diffuse_intensity = 1.0
            material.specular_intensity = 0.0

            # TODO: search backwards until we hit the "data" directory (or slough off bits until we
            # hit hte data directory?)
            data_path = rtrim_path_until(dirname, 'data')

            ''' Create texture. '''
            texture = bpy.data.textures.new(texture_path, type='IMAGE')

            if data_path != '':
                texpath = os.path.join(data_path, 'texture', texture_path)
                try:
                    texture.image = bpy.data.images.load(texpath, check_existing=True)
                except RuntimeError:
                    pass

            texture_slot = material.texture_slots.add()
            texture_slot.texture = texture

            materials.append(material)

        nodes = {}
        for node in rsm.nodes:
            mesh = bpy.data.meshes.new(node.name)
            mesh_object = bpy.data.objects.new(node.name, mesh)

            nodes[node.name] = mesh_object

            if node.parent_name in nodes:
                mesh_object.parent = nodes[node.parent_name]

            ''' Add UV map to each material. '''
            uv_texture = mesh.uv_textures.new()
            material.texture_slots[0].uv_layer = uv_texture.name


            bm = bmesh.new()
            bm.from_mesh(mesh)

            for texture_index in node.texture_indices:
                mesh.materials.append(materials[texture_index])

            for vertex in node.vertices:
                bm.verts.new(vertex)

            bm.verts.ensure_lookup_table()

            # TODO: texture slots

            for face in node.faces:
                bmface = bm.faces.new([bm.verts[x] for x in face.vertex_indices])
                bmface.material_index = face.texture_index

            bm.faces.ensure_lookup_table()

            bm.to_mesh(mesh)

            '''
            Assign texture coordinates.
            '''
            uv_texture = mesh.uv_layers[0]
            for face_index, face in enumerate(node.faces):
                uvs = [node.texcoords[x] for x in face.texcoord_indices]
                for i, uv in enumerate(uvs):
                    # UVs have to be V-flipped (maybe)
                    uv = uv[1:]
                    uv = uv[0], 1.0 - uv[1]
                    uv_texture.data[face_index * 3 + i].uv = uv

            bpy.context.scene.objects.link(mesh_object)

            offset = (node.offset[0], node.offset[2], node.offset[1] * -1.0)

            mesh_object.location = offset
        return nodes[rsm.main_node]

    def execute(self, context):
        RsmImportOperator.import_rsm(self.filepath)
        return {'FINISHED'}

    @staticmethod
    def menu_func_import(self, context):
        self.layout.operator(RsmImportOperator.bl_idname, text='Ragnarok Online RSM (.rsm)')
