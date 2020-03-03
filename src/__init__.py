bl_info = {
    'name': 'Ragnarok Online Importers',
    'description': 'Import RSW, RSM and GND files from Ragnarok Online.',
    'author': 'Colin Basnett',
    'version': (1, 0, 0),
    'blender': (2, 80, 0),
    'location': 'File > Import-Export',
    'warning': 'This add-on is under development.',
    'wiki_url': 'https://github.com/cmbasnett/io_scene_rsw/wiki',
    'tracker_url': 'https://github.com/cmbasnett/io_scene_rsw/issues',
    'support': 'COMMUNITY',
    'category': 'Import-Export'
}

if 'bpy' in locals():
    import importlib
    if 'gnd'            in locals(): importlib.reload(gnd)
    if 'rsm'            in locals(): importlib.reload(rsm)
    if 'rsw'            in locals(): importlib.reload(rsw)
    if 'gnd_importer'   in locals(): importlib.reload(gnd_importer)
    if 'rsm_importer'   in locals(): importlib.reload(rsm_importer)
    if 'rsw_importer'   in locals(): importlib.reload(rsw_importer)

import bpy
from .gnd import gnd
from .rsm import rsm
from .rsw import rsw
from .gnd import importer as gnd_importer
from .rsm import importer as rsm_importer
from .rsw import importer as rsw_importer

classes = (
    gnd_importer.GND_OT_ImportOperator,
    rsm_importer.RSM_OT_ImportOperator,
    rsw_importer.RSW_OT_ImportOperator,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(gnd_importer.GND_OT_ImportOperator.menu_func_import)
    bpy.types.TOPBAR_MT_file_import.append(rsm_importer.RSM_OT_ImportOperator.menu_func_import)
    bpy.types.TOPBAR_MT_file_import.append(rsw_importer.RSW_OT_ImportOperator.menu_func_import)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.TOPBAR_MT_file_import.remove(gnd_importer.GND_OT_ImportOperator.menu_func_import)
    bpy.types.TOPBAR_MT_file_import.remove(rsm_importer.RSM_OT_ImportOperator.menu_func_import)
    bpy.types.TOPBAR_MT_file_import.remove(rsw_importer.RSW_OT_ImportOperator.menu_func_import)

    for cls in classes:
        bpy.utils.unregister_class(cls)
