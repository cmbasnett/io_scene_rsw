import os
import bpy
import bpy_extras
import bmesh
# import os
# import math
# from mathutils import Vector, Matrix, Quaternion
from bpy.props import StringProperty, BoolProperty, FloatProperty
from .gnd.reader import GndReader
from .rsm.reader import RsmReader


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

    def execute(self, context):
        gnd = GndReader.from_file(self.filepath)
        name = os.path.splitext(os.path.basename(self.filepath))[0]
        mesh = bpy.data.meshes.new(name)
        mesh_object = bpy.data.objects.new(name, mesh)

        dirname = os.path.dirname(self.filepath)
        print(dirname)

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

            data_path = rtrim_path_until(dirname, 'data')

            print('data path')
            print(data_path)

            texpath = os.path.join(data_path, 'texture', texture_path)
            try:
                texture.image = bpy.data.images.load(texpath, check_existing=True)
            except RuntimeError:
                pass

            texture_slot = material.texture_slots.add()
            texture_slot.texture = texture

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
        for material in materials:
            ''' Create UV map. '''
            mesh.materials.append(material)
            material.texture_slots[0].uv_layer = uv_texture.name

        '''
        Assign texture coordinates.
        '''
        uv_texture = mesh.uv_layers[0]
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

        bpy.context.scene.objects.link(mesh_object)
        return {'FINISHED'}

    @staticmethod
    def menu_func_import(self, context):
        self.layout.operator(GndImportOperator.bl_idname, text='Ragnarok Online GND (.gnd)')



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


    def execute(self, context):
        rsm = RsmReader.from_file(self.filepath)
        dirname = os.path.dirname(self.filepath)

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

        return {'FINISHED'}

    @staticmethod
    def menu_func_import(self, context):
        self.layout.operator(RsmImportOperator.bl_idname, text='Ragnarok Online RSM (.rsm)')
