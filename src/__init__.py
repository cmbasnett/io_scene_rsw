if __name__ != 'src':  # TODO: temp
    bl_info = {
        'name': 'Ragnarok Online GND Format',
        'description': 'Import GND files from Ragnarok Online.',
        'author': 'Colin Basnett',
        'version': (1, 0, 0),
        'blender': (2, 79, 0),
        'location': 'File > Import-Export',
        'warning': 'This add-on is under development.',
        'wiki_url': 'https://github.com/cmbasnett/io_scene_rsw/wiki',
        'tracker_url': 'https://github.com/cmbasnett/io_scene_rsw/issues',
        'support': 'COMMUNITY',
        'category': 'Import-Export'
    }

    if 'bpy' in locals():
        import importlib
        if 'gnd'        in locals(): importlib.reload(gnd)
        if 'rsm'        in locals(): importlib.reload(rsm)
        if 'importer'   in locals(): importlib.reload(importer)

    import bpy
    from .gnd import gnd
    from .rsm import rsm
    from . import importer

    def register():
        bpy.utils.register_module(__name__)
        bpy.types.INFO_MT_file_import.append(importer.GndImportOperator.menu_func_import)
        bpy.types.INFO_MT_file_import.append(importer.RsmImportOperator.menu_func_import)


    def unregister():
        bpy.utils.unregister_module(__name__)
        bpy.types.INFO_MT_file_import.remove(importer.GndImportOperator.menu_func_import)
        bpy.types.INFO_MT_file_import.remove(importer.RsmImportOperator.menu_func_import)
