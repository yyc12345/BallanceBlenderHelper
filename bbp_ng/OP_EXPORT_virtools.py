import bpy
from . import PROP_preferences, UTIL_functions, UTIL_file_browser, UTIL_blender_mesh
from .PyBMap import bmap_wrapper as bmap

class BBP_OT_export_virtools(bpy.types.Operator, UTIL_file_browser.ExportVirtoolsFile):
    """Export Virtools File"""
    bl_idname = "bbp.export_virtools"
    bl_label = "Export Virtools File"
    bl_options = {'PRESET'}

    @classmethod
    def poll(self, context):
        return (
            PROP_preferences.get_raw_preferences().has_valid_blc_tex_folder()
            and bmap.is_bmap_available())
    
    def execute(self, context):
        UTIL_functions.message_box((self.general_get_filename(), ), 'Export Virtools File Path', 'INFO')
        self.report({'INFO'}, "Virtools File Exporting Finished.")
        return {'FINISHED'}
    
    def draw(self, context):
        pass

def register() -> None:
    bpy.utils.register_class(BBP_OT_export_virtools)

def unregister() -> None:
    bpy.utils.unregister_class(BBP_OT_export_virtools)
