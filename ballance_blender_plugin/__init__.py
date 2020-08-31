bl_info={
	"name":"Ballance Blender Plugin",
	"description":"Ballance mapping tools for Blender",
	"author":"yyc12345",
	"version":(1,0),
	"blender":(2,83,0),
	"category":"Object",
	"support":"TESTING",
    "warning": "Please read document before using this plugin.",
    "wiki_url": "https://github.com/yyc12345/BallanceBlenderHelper",
    "tracker_url": "https://github.com/yyc12345/BallanceBlenderHelper/issues"
}

# ============================================= import system
import bpy,bpy_extras
# import my code (with reload)
if "bpy" in locals():
    import importlib
    if "bm_import_export" in locals():
        importlib.reload(bm_import_export)
    if "rail_uv" in locals():
        importlib.reload(rail_uv)
    if "utils" in locals():
        importlib.reload(utils)
    if "config" in locals():
        importlib.reload(config)
    if "preferences" in locals():
        importlib.reload(preferences)
    if "threedsmax_align" in locals():
        importlib.reload(threedsmax_align)
    if "no_uv_checker" in locals():
        importlib.reload(no_uv_checker)
from . import config, utils, bm_import_export, rail_uv, preferences, threedsmax_align, no_uv_checker

# ============================================= menu system

class ThreeDViewerMenu(bpy.types.Menu):
    """Ballance related 3D operator"""
    bl_label = "Ballance 3D"
    bl_idname = "OBJECT_MT_ballance3d_menu"

    def draw(self, context):
        layout = self.layout

        layout.operator("ballance.threedsmax_align")
        layout.operator("ballance.rail_uv")
        layout.operator("ballance.no_uv_checker")

# ============================================= blender call system

classes = (
    preferences.BallanceBlenderPluginPreferences,
    bm_import_export.ImportBM,
    bm_import_export.ExportBM,
    rail_uv.RailUVOperator,
    threedsmax_align.SuperAlignOperator,
    no_uv_checker.NoUVCheckerOperator,
    ThreeDViewerMenu
)

def menu_func_bm_import(self, context):
    self.layout.operator(bm_import_export.ImportBM.bl_idname, text="Ballance Map (.bm)")
def menu_func_bm_export(self, context):
    self.layout.operator(bm_import_export.ExportBM.bl_idname, text="Ballance Map (.bm)")
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