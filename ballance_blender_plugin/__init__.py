bl_info={
	"name":"Ballance Blender Plugin",
	"description":"Ballance mapping tools for Blender",
	"author":"yyc12345",
	"version":(1,1),
	"blender":(2,83,0),
	"category":"Object",
	"support":"TESTING",
    "warning": "Please read document before using this plugin.",
    "wiki_url": "https://github.com/yyc12345/BallanceBlenderHelper",
    "tracker_url": "https://github.com/yyc12345/BallanceBlenderHelper/issues"
}

# ============================================= import system
import bpy,bpy_extras
import bpy.utils.previews
import os
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
    if "add_elements" in locals():
        importlib.reload(add_elements)
    if "add_floor" in locals():
        importlib.reload(add_floor)
from . import config, utils, bm_import_export, rail_uv, preferences, threedsmax_align, no_uv_checker, add_elements, add_floor

# ============================================= menu system

class BALLANCE_MT_ThreeDViewerMenu(bpy.types.Menu):
    """Ballance related 3D operator"""
    bl_idname = "BALLANCE_MT_ThreeDViewerMenu"
    bl_label = "Ballance 3D"

    def draw(self, context):
        layout = self.layout

        layout.operator("ballance.super_align")
        layout.operator("ballance.rail_uv")
        layout.operator("ballance.no_uv_checker")

class BALLANCE_MT_AddFloorMenu(bpy.types.Menu):
    """Add Ballance floor"""
    bl_idname = "BALLANCE_MT_AddFloorMenu"
    bl_label = "Floors"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Basic floor")
        for item in config.floor_basic_block_list:
            cop = layout.operator("ballance.add_floor", text=item, icon_value = config.blenderIcon_floor_dict[item])
            cop.floor_type = item

        layout.separator()
        layout.label(text="Derived floor")
        for item in config.floor_derived_block_list:
            cop = layout.operator("ballance.add_floor", text=item, icon_value = config.blenderIcon_floor_dict[item])
            cop.floor_type = item


# ============================================= blender call system

classes = (
    preferences.BallanceBlenderPluginPreferences,
    preferences.MyPropertyGroup,
    
    bm_import_export.BALLANCE_OT_import_bm,
    bm_import_export.BALLANCE_OT_export_bm,
    rail_uv.BALLANCE_OT_rail_uv,
    threedsmax_align.BALLANCE_OT_super_align,
    no_uv_checker.BALLANCE_OT_no_uv_checker,
    BALLANCE_MT_ThreeDViewerMenu,

    add_elements.BALLANCE_OT_add_elements,
    add_elements.BALLANCE_OT_add_rail,
    add_floor.BALLANCE_OT_add_floor,
    BALLANCE_MT_AddFloorMenu
)

def menu_func_bm_import(self, context):
    self.layout.operator(bm_import_export.BALLANCE_OT_import_bm.bl_idname, text="Ballance Map (.bmx)")
def menu_func_bm_export(self, context):
    self.layout.operator(bm_import_export.BALLANCE_OT_export_bm.bl_idname, text="Ballance Map (.bmx)")
def menu_func_ballance_3d(self, context):
    layout = self.layout
    layout.menu(BALLANCE_MT_ThreeDViewerMenu.bl_idname)
def menu_func_ballance_add(self, context):
    layout = self.layout
    layout.separator()
    layout.label(text="Ballance")
    layout.operator_menu_enum("ballance.add_elements", "elements_type", icon='MESH_ICOSPHERE', text="Elements")
    layout.operator("ballance.add_rail", icon='MESH_CIRCLE', text="Rail section")
    layout.menu(BALLANCE_MT_AddFloorMenu.bl_idname, icon='MESH_CUBE')

def register():
    # we need init all icon first
    icon_path = os.path.join(os.path.dirname(__file__), "icons")
    config.blenderIcon_floor = bpy.utils.previews.new()
    for key, value in config.floor_block_dict.items():
        blockIconName = "Ballance_FloorIcon_" + key
        config.blenderIcon_floor.load(blockIconName, os.path.join(icon_path, "floor", value["BindingDisplayTexture"]), 'IMAGE')
        config.blenderIcon_floor_dict[key] = config.blenderIcon_floor[blockIconName].icon_id

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.BallanceBlenderPluginProperty = bpy.props.PointerProperty(type=preferences.MyPropertyGroup)
        
    bpy.types.TOPBAR_MT_file_import.append(menu_func_bm_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_bm_export)

    bpy.types.VIEW3D_HT_header.append(menu_func_ballance_3d)
    bpy.types.VIEW3D_MT_add.append(menu_func_ballance_add)
        
def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_bm_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_bm_export)
    
    bpy.types.VIEW3D_HT_header.remove(menu_func_ballance_3d)
    bpy.types.VIEW3D_MT_add.remove(menu_func_ballance_add)

    for cls in classes:
        bpy.utils.unregister_class(cls)

    # we need uninstall all icon after all classes unregister
    bpy.utils.previews.remove(config.blenderIcon_floor)
    
if __name__=="__main__":
	register()