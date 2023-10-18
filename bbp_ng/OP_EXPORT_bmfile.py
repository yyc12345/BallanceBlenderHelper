import bpy
from . import PROP_preferences, UTIL_functions, UTIL_file_browser, UTIL_blender_mesh

class BBP_OT_export_bmfile(bpy.types.Operator, UTIL_file_browser.ExportBmxFile):
    """Save a Ballance Map File (BM File Spec 1.4)"""
    bl_idname = "bbp.export_bmfile"
    bl_label = "Export BM (Ballance Map) File"
    bl_options = {'PRESET'}

    @classmethod
    def poll(self, context):
        return PROP_preferences.get_raw_preferences().has_valid_blc_tex_folder()
    
    def execute(self, context):
        UTIL_functions.message_box((self.general_get_filename(), ), 'Export BM File Path', 'INFO')
        self.report({'INFO'}, "BM File Exporting Finished.")
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout

def register() -> None:
    bpy.utils.register_class(BBP_OT_export_bmfile)

def unregister() -> None:
    bpy.utils.unregister_class(BBP_OT_export_bmfile)
