bl_info={
	"name":"Ballance Blender Plugin",
	"description":"Ballance mapping tools for Blender",
	"author":"yyc12345",
	"version":(0,1),
	"blender":(2,83,0),
	"category":"Object",
	"support":"TESTING"
}

# import system
import bpy,bpy_extras
# import my code (with reload)
if "bpy" in locals():
    import importlib
    if "bm_import_export" in locals():
        importlib.reload(bm_import_export)
from . import bm_import_export

class ImportBM(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Load a Ballance Map File"""
    bl_idname = "import_scene.bm"
    bl_label = "Import BM"
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".bm"

    def execute(self, context):
        bm_import_export.import_bm(context, self.filepath)
        return {'FINISHED'}
        
class ExportBM(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Save a Ballance Map File"""
    bl_idname = "export_scene.bm"
    bl_label = 'Export BM'
    bl_options = {'PRESET'}
    filename_ext = ".bm"
    
    export_mode: bpy.props.EnumProperty(
        name="Export mode",
        items=(('COLLECTION', "Selected collection", "Export the selected collection"),
               ('OBJECT', "Selected objects", "Export the selected objects"),
               ),
        )
    export_target: bpy.props.StringProperty(
        name="Export target",
        description="Which one will be exported",
        )
    no_component_suffix: bpy.props.StringProperty(
        name="No component suffix",
        description="The object which have this suffix will not be saved as component.",
        )
    
    def execute(self, context):
        bm_import_export.export_bm(context, self.filepath, self.export_mode, self.export_target, self.no_component_suffix)
        return {'FINISHED'}
        
classes = (
    ImportBM,
    ExportBM
)

def menu_func_bm_import(self, context):
    self.layout.operator(ImportBM.bl_idname, text="Ballance Map (.bm)")


def menu_func_bm_export(self, context):
    self.layout.operator(ExportBM.bl_idname, text="Ballance Map (.bm)")


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.TOPBAR_MT_file_import.append(menu_func_bm_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_bm_export)
        
def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_bm_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_bm_export)
    
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
if __name__=="__main__":
	register()