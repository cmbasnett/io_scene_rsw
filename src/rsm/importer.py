import os
import bpy
import bpy_extras
import bmesh
import math
import mathutils
from mathutils import Vector, Matrix, Quaternion
from bpy.props import StringProperty, BoolProperty, FloatProperty
from ..utils.utils import get_data_path
from ..rsm.reader import RsmReader


class RsmImportOptions(object):
    def __init__(self, should_import_smoothing_groups:bool = True):
        self.should_import_smoothing_groups = should_import_smoothing_groups

class RSM_OT_ImportOperator(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = 'io_scene_rsw.rsm_import'  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = 'Import Ragnarok Online RSM'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    filename_ext = ".rsm"

    filter_glob: StringProperty(
        default="*.rsm",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    should_import_smoothing_groups: BoolProperty(
        default=True
    )

    @staticmethod
    def set_origin_to_bottom(obj):
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # 1. Move the cursor to the lowest point of the boundary box to position the model correctly, as in the game.
        mw = obj.matrix_world
        local_bbox = [obj.matrix_world @ mathutils.Vector(v) for v in obj.bound_box]
        bottom_z = min(v.z for v in local_bbox)
        center_x = sum(v.x for v in local_bbox) / 8
        center_y = sum(v.y for v in local_bbox) / 8
        
        bpy.context.scene.cursor.location = (center_x, center_y, bottom_z)
        
        # 2. ย้าย Origin ไปที่ Cursor
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        obj.select_set(False)

    @staticmethod
    def import_rsm(filepath, options):
        rsm = RsmReader.from_file(filepath)
        name = os.path.basename(filepath)
        data_path = get_data_path(filepath)
        materials = []

        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)

        for texture_path in rsm.textures:
            # png_texture_path = texture_path[:-3] + "png"
            png_texture_path = texture_path
            
            material = bpy.data.materials.new(png_texture_path)
            material.specular_intensity = 0.0
            material.use_nodes = True
            materials.append(material)

            # TODO: search backwards until we hit the "data" directory (or slough off bits until we
            # hit hte data directory?)

            ''' Create texture. '''
            bsdf = material.node_tree.nodes['Principled BSDF']
            if 'Specular IOR Level' in bsdf.inputs:
                bsdf.inputs['Specular IOR Level'].default_value = 0.0
            else:
                bsdf.inputs['Specular'].default_value = 0.0
            texImage = material.node_tree.nodes.new('ShaderNodeTexImage')

            material.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
            # material.node_tree.links.new(bsdf.inputs['Alpha'], texImage.outputs['Alpha'])

            ''' Load texture. '''
            texpath = os.path.join(data_path, 'texture', png_texture_path)

            try:
                texImage.image = bpy.data.images.load(texpath, check_existing=True)
            except RuntimeError:
                pass

        nodes = {}
        for node in rsm.nodes:
            mesh = bpy.data.meshes.new(node.name)
            mesh_object = bpy.data.objects.new(os.path.relpath(filepath, data_path), mesh)

            nodes[node.name] = mesh_object

            if node.parent_name in nodes:
                mesh_object.parent = nodes[node.parent_name]

            ''' Add UV map to each material. '''
            uv_layer = mesh.uv_layers.new()

            bm = bmesh.new()
            bm.from_mesh(mesh)

            for texture_index in node.texture_indices:
                mesh.materials.append(materials[texture_index])

            for vertex in node.vertices:
                bm.verts.new(vertex)

            bm.verts.ensure_lookup_table()

            '''
            Build smoothing group face look-up-table.
            '''
            actual_face_index = 0
            smoothing_group_faces = dict()
            for face_index, face in enumerate(node.faces):
                try:
                    bmface = bm.faces.new([bm.verts[x] for x in face.vertex_indices])
                    bmface.material_index = face.texture_index
                except ValueError as e:
                    bmface = None
                except Exception as e:
                    print(f"Skipping a face due to error: {e}")
                if options.should_import_smoothing_groups:
                    if bmface:
                        bmface.smooth = True
                    if face.smoothing_group not in smoothing_group_faces:
                        smoothing_group_faces[face.smoothing_group] = []
                    smoothing_group_faces[face.smoothing_group].append(actual_face_index)
                actual_face_index += 1

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
                    try:
                        uv_texture.data[face_index * 3 + i].uv = uv
                    except IndexError as e:
                        print(f"Skipping uv_texture IndexError error: {e}")

            '''
            Apply transforms.
            '''
            offset = Vector((node.offset[0], node.offset[2], node.offset[1] * -1.0))

            if mesh_object.parent is None:
                mesh_object.location = offset * -1
            else:
                mesh_object.location = offset

            mesh_object.scale = node.scale

            collection.objects.link(mesh_object)

            '''
            Apply smoothing groups.
            '''
            if options.should_import_smoothing_groups:
                bpy.ops.object.select_all(action='DESELECT')
                mesh_object.select_set(True)
                bpy.context.view_layer.objects.active = mesh_object
                for smoothing_group, face_indices in smoothing_group_faces.items():
                    '''
                    Select all faces in the smoothing group.
                    '''
                    bpy.ops.object.mode_set(mode='OBJECT')
                    for face_index in face_indices:
                        try:
                            mesh.polygons[face_index].select = True
                        except IndexError as e:
                            print(f"Skipping face_index IndexError error: {e}")
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_mode(type='FACE')
                    '''
                    Mark boundary edges as sharp.
                    '''
                    bpy.ops.mesh.region_to_loop()
                    bpy.ops.mesh.mark_sharp()
                bpy.ops.object.mode_set(mode='OBJECT')
                '''
                Add edge split modifier.
                '''
                edge_split_modifier = mesh_object.modifiers.new('EdgeSplit', type='EDGE_SPLIT')
                edge_split_modifier.use_edge_angle = False
                edge_split_modifier.use_edge_sharp = True
                bpy.ops.object.select_all(action='DESELECT')

        main_node = nodes[rsm.main_node]
        if main_node is not None:
            bpy.ops.object.select_all(action='DESELECT')
            mesh_object.select_set(True)
            bpy.context.view_layer.objects.active = mesh_object
            bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)
            mesh_object.select_set(False)
            RSM_OT_ImportOperator.set_origin_to_bottom(main_node)
            bpy.ops.object.select_all(action='DESELECT')

        return nodes[rsm.main_node]

    def execute(self, context):
        options = RsmImportOptions(
            should_import_smoothing_groups=self.should_import_smoothing_groups
        )
        RSM_OT_ImportOperator.import_rsm(self.filepath, options)
        return {'FINISHED'}



    @staticmethod
    def menu_func_import(self, context):
        self.layout.operator(RSM_OT_ImportOperator.bl_idname, text='Ragnarok Online RSM (.rsm)')
