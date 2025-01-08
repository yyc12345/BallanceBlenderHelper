import bpy
from . import PROP_preferences, UTIL_functions, UTIL_file_browser, UTIL_blender_mesh, UTIL_ioport_shared

class BBP_OT_import_bmfile(bpy.types.Operator, UTIL_file_browser.ImportBmxFile, UTIL_ioport_shared.ImportParams):
    """Load a Ballance Map File (BM File Spec 1.4)"""
    bl_idname = "bbp.import_bmfile"
    bl_label = "Import BM (Ballance Map) File"
    bl_options = {'PRESET', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return PROP_preferences.get_raw_preferences().has_valid_blc_tex_folder()
    
    def execute(self, context):
        self.report({'ERROR'}, 'This function not supported yet.')
        # self.report({'INFO'}, "BM File Importing Finished.")
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        layout.label(text = 'Conflict Options')
        self.draw_import_params(layout.box())

def register() -> None:
    bpy.utils.register_class(BBP_OT_import_bmfile)

def unregister() -> None:
    bpy.utils.unregister_class(BBP_OT_import_bmfile)
