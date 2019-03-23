import bpy
import bpy_extras
# import bmesh
# import os
# import math
# from mathutils import Vector, Matrix, Quaternion
from bpy.props import StringProperty, BoolProperty, FloatProperty
# from .dtx import DTX
# from .reader import ModelReader
# from . import utils

class ImportOperator(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
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

    def execute(self, context):
        rsw = RswReader.from_file(self.filepath)
        return {'FINISHED'}

    @staticmethod
    def menu_func_import(self, context):
        self.layout.operator(ImportOperator.bl_idname, text='Ragnarok Online RSW (.rsw)')
