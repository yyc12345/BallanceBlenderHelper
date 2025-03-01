import bpy
from . import PROP_preferences, UTIL_functions, UTIL_file_browser, UTIL_blender_mesh, UTIL_ioport_shared

class BBP_OT_export_bmfile(bpy.types.Operator, UTIL_file_browser.ExportBmxFile, UTIL_ioport_shared.ExportParams):
    """Save a Ballance Map File (BM File Spec 1.4)"""
    bl_idname = "bbp.export_bmfile"
    bl_label = "Export BM (Ballance Map) File"
    bl_options = {'PRESET'}
    bl_translation_context = 'BBP_OT_export_bmfile'

    @classmethod
    def poll(cls, context):
        return PROP_preferences.get_raw_preferences().has_valid_blc_tex_folder()
    
    def execute(self, context):
        self.report({'ERROR'}, 'This feature is not supported yet.')
        # self.report({'INFO'}, "BM File Exporting Finished.")
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        self.draw_export_params(context, layout.box())

def register() -> None:
    bpy.utils.register_class(BBP_OT_export_bmfile)

def unregister() -> None:
    bpy.utils.unregister_class(BBP_OT_export_bmfile)
