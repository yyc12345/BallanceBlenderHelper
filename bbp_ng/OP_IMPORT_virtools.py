import bpy
from . import PROP_preferences, UTIL_functions, UTIL_file_browser, UTIL_blender_mesh

class BBP_OT_import_virtools(bpy.types.Operator, UTIL_file_browser.ImportVirtoolsFile):
    """Import Virtools File"""
    bl_idname = "bbp.import_virtools"
    bl_label = "Import Virtools File"
    bl_options = {'PRESET', 'UNDO'}

    @classmethod
    def poll(self, context):
        return PROP_preferences.get_raw_preferences().has_valid_blc_tex_folder()
    
    def execute(self, context):
        UTIL_functions.message_box((self.general_get_filename(), ), 'Import Virtools File Path', 'INFO')
        self.report({'INFO'}, "Virtools File Importing Finished.")
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout

def register() -> None:
    bpy.utils.register_class(BBP_OT_import_virtools)

def unregister() -> None:
    bpy.utils.unregister_class(BBP_OT_import_virtools)
