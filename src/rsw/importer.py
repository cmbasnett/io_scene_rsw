import os
import bpy
import bpy_extras
import math
from mathutils import Vector, Matrix, Quaternion
from bpy.props import StringProperty, BoolProperty, FloatProperty
from ..utils.utils import get_data_path
from ..rsw.reader import RswReader
from ..gnd.importer import GndImportOptions, GND_OT_ImportOperator
from ..rsm.importer import RsmImportOptions, RSM_OT_ImportOperator

class RSW_OT_ImportOperator(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = 'io_scene_rsw.rsw_import'  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = 'Import Ragnarok Online RSW'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    filename_ext = ".rsw"

    scale_factor = 0.1

    filter_glob: StringProperty(
        default="*.rsw",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    data_path: StringProperty(
        default='',
        maxlen=255,
        subtype='DIR_PATH'
    )

    should_import_gnd: BoolProperty(default=True)
    should_import_models: BoolProperty(default=True)

    def execute(self, context):
        # Load the RSW file
        rsw = RswReader.from_file(self.filepath)
        
        self.report({'INFO'}, f'Loaded RSW version: {rsw.rsw_version.major}.{rsw.rsw_version.minor}')

        # Find the data path.
        data_path = get_data_path(self.filepath)

        # TODO: create an EMPTY object that is the RSW parent object
        name = os.path.basename(self.filepath)

        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)

        # Load the GND file and import it into the scene.
        gnd_x_width = 0
        gnd_y_height = 0
        gnd_z_depth = 0
        
        if self.should_import_gnd:
            gnd_path = os.path.join(data_path, rsw.gnd_file)
            try:
                options = GndImportOptions()
                gnd_object = GND_OT_ImportOperator.import_gnd(gnd_path, options)
            except FileNotFoundError:
                try:
                    gnd_path = gnd_path + name[:-4] + '.gnd'
                    options = GndImportOptions()
                    gnd_object = GND_OT_ImportOperator.import_gnd(gnd_path, options)
                except FileNotFoundError:
                    self.report({'ERROR'}, 'GND file ({}) could not be found in directory ({}).'.format(rsw.gnd_file, data_path))
                    return {'CANCELLED'}
            gnd_x_width = gnd_object.dimensions[0]
            gnd_y_height = gnd_object.dimensions[1]
            gnd_z_depth = gnd_object.dimensions[2]
            scale_x, scale_z, scale_y = gnd_object.scale
            gnd_object.scale = Vector((scale_x * self.scale_factor, scale_y * self.scale_factor, scale_z * self.scale_factor))
            gnd_object.location = Vector((0, 0, 0))
            collection.objects.link(gnd_object)

            
        # set position of gnd object
        if gnd_x_width > 0:
            gnd_x_width = gnd_x_width /2
        if gnd_y_height > 0:
            gnd_y_height = gnd_y_height /2
        if gnd_z_depth > 0:
            gnd_z_depth = gnd_z_depth /2

        if self.should_import_models:
            # Load up all the RSM files and import them into the scene.
            models_path = os.path.join(data_path, 'model')
            rsm_options = RsmImportOptions()
            model_data = dict()
            for rsw_model in rsw.models:
                if rsw_model.filename in model_data:
                    model_object = bpy.data.objects.new(rsw_model.name, model_data[rsw_model.filename])
                else:
                    # Converts Windows filename separators to the OS's path separator
                    filename = rsw_model.filename.replace('\\', os.path.sep)
                    rsm_path = os.path.join(models_path, filename)
                    try:
                        model_object = RSM_OT_ImportOperator.import_rsm(rsm_path, rsm_options)
                        model_data[rsw_model.filename] = model_object.data
                    except FileNotFoundError:
                        self.report({'ERROR'}, 'RSM file ({}) could not be found in directory ({}).'.format(filename, models_path))
                        return {'CANCELLED'}

                x, z, y = rsw_model.position
                model_object.location = Vector(((x + gnd_x_width) * self.scale_factor, (y + gnd_y_height) * self.scale_factor, -z * self.scale_factor))
                rotation_x, rotation_z, rotation_y = rsw_model.rotation
                model_object.rotation_euler = (math.radians(rotation_x), math.radians(rotation_y), math.radians(-rotation_z))
                scale_x, scale_z, scale_y = rsw_model.scale
                model_object.scale = Vector((scale_x * self.scale_factor, scale_y * self.scale_factor, scale_z * self.scale_factor))
                collection.objects.link(model_object)
        return {'FINISHED'}

    @staticmethod
    def menu_func_import(self, context):
        self.layout.operator(RSW_OT_ImportOperator.bl_idname, text='Ragnarok Online RSW (.rsw)')
