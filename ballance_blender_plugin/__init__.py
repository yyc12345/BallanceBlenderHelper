bl_info={
	"name":"Ballance Blender Plugin",
	"description":"Ballance mapping tools for Blender",
	"author":"yyc12345",
	"version":(0,1),
	"blender":(2,83,0),
	"category":"Object",
	"support":"TESTING"
}

# ============================================= import system
import bpy,bpy_extras
# import my code (with reload)
if "bpy" in locals():
    import importlib
    if "bm_import_export" in locals():
        importlib.reload(bm_import_export)
    if "floor_rail_uv" in locals():
        importlib.reload(floor_rail_uv)
    if "utils" in locals():
        importlib.reload(utils)
from . import utils, bm_import_export, floor_rail_uv

# ============================================= func block

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

# ============================================= menu system

class RailUVOperator(bpy.types.Operator):
    """Create a UV for rail"""
    bl_idname = "ballance.rail_uv"
    bl_label = "Create Rail UV"
    bl_options = {'UNDO'}

    def execute(self, context):
        floor_rail_uv.create_rail_uv()
        return {'FINISHED'}

class FloorUVOperator(bpy.types.Operator):
    """Virtoolize the UV of floor"""
    bl_idname = "ballance.floor_uv"
    bl_label = "Virtoolize floor UV"
    bl_options = {'UNDO'}

    def execute(self, context):
        floor_rail_uv.virtoolize_floor_uv()
        return {'FINISHED'}

class ThreeDViewerMenu(bpy.types.Menu):
    bl_label = "Ballance 3D"
    bl_idname = "OBJECT_MT_ballance3d_menu"

    def draw(self, context):
        layout = self.layout

        layout.operator("ballance.rail_uv")
        layout.operator("ballance.floor_uv")

# ============================================= blender call system

classes = (
    ImportBM,
    ExportBM,
    RailUVOperator,
    FloorUVOperator,
    ThreeDViewerMenu
)

def menu_func_bm_import(self, context):
    self.layout.operator(ImportBM.bl_idname, text="Ballance Map (.bm)")
def menu_func_bm_export(self, context):
    self.layout.operator(ExportBM.bl_idname, text="Ballance Map (.bm)")
def menu_func_ballance_3d(self, context):
    layout = self.layout
    layout.menu(ThreeDViewerMenu.bl_idname)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.TOPBAR_MT_file_import.append(menu_func_bm_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_bm_export)

    bpy.types.VIEW3D_HT_header.append(menu_func_ballance_3d)
        
def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_bm_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_bm_export)
    
    bpy.types.VIEW3D_HT_header.remove(menu_func_ballance_3d)

    for cls in classes:
        bpy.utils.unregister_class(cls)
    
if __name__=="__main__":
	register()